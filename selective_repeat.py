from stop_and_wait import Sender, Receiver, Event, EventLoop
from go_back_N import GBN_Sender, GBN_Receiver
import numpy as np
import random


class SR_Sender(GBN_Sender):
    def __init__(self, bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop, window_size):
        super().__init__(bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop, window_size)
        self.resend_queue = []

    def send_frame(self, receiver):
        frame = -1
        # check whether resend is need
        if len(self.resend_queue) != 0:
            frame = self.latest_unacked_frame
            self.resend_queue.pop()  # should be only 1 elements in the queue
            # seletive repeat
            pass
        else:
            if self.next_frame - self.latest_unacked_frame >= self.window_size:
                pass
                # do something
            if self.send_window[self.next_frame] == -1:
                self.load_frames()
            frame = self.frames[self.next_frame]

            if frame == -1:
                # No frame to send
                return
            self.next_frame = (self.next_frame + 1) % self.window_size
        transmission_time = self.frame_size / (self.bandwidth * 1e6)
        propagation_time = self.delay / 1000
        total_time = transmission_time + propagation_time
        timeout = 2 * total_time

        print('send %d %d' % (self.next_frame, frame))
        if random.random() > self.frame_error_rate:
            print('frame %d sent.' % self.next_frame)
            self.event_loop.add_event(
                Event(receiver.receive_frame, event_loop.current_time + total_time, frame, self))

        self.event_loop.add_event(
            Event(self.handle_timeout, event_loop.current_time + timeout, receiver, self.next_frame))

    def handle_ack(self, receiver, ack):
        pass


class SR_Receiver(Receiver):
    def __init__(self, bandwidth, delay, bit_error_rate, ack_size, event_loop):
        super().__init__(bandwidth, delay, bit_error_rate, ack_size, event_loop)
        self.unreceived_frames = []

    def receive_frame(self, frame, sender):
        # extract the one bit frame sequence number and compare to the expected frame number
        if frame == self.expected_frame:
            if frame in self.unreceived_frames:
                self.unreceived_frames.remove(frame)
            self.received_frames.append(frame)

            if len(self.unreceived_frames) == 0:
                self.expected_frame = len(self.received_frames)
            else:
                self.unreceived_frames.sort()  # Maybe not necessary
                self.expected_frame = self.unreceived_frames[0]
            self.send_ack(sender)
        else:
            self.received_frames.append(frame)
            for i in range(self.expected_frame, frame):
                if i not in self.received_frames:
                    self.unreceived_frames.append(i)
            self.send_ack(sender)

    def send_ack(self, sender):
        transmission_time = self.ack_size / (self.bandwidth * 1e6)
        propagation_time = self.delay / 1000
        total_time = transmission_time + propagation_time
        self.event_loop.add_event(
            Event(sender.handle_ack, event_loop.current_time + total_time, self, self.expected_frame))


if __name__ == "__main__":
    time_limit = 1 * 60  # seconds

    bandwidth = 1  # Mbps
    delay = 100  # ms
    bit_error_rate = 1e-5
    frame_size = 1250 * 8  # bits
    ack_size = 25 * 8  # bits
    header_size = 25 * 8  # bit
    num_frames = 1000000
    window_size = 4

    event_loop = EventLoop()
    sender = GBN_Sender(bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop, window_size)
    receiver = GBN_Receiver(bandwidth, delay, bit_error_rate, ack_size, event_loop, window_size)

    # Add the initial event to generate all frames
    sender.generate_all_frames(num_frames)
    event_loop.add_event(Event(sender.send_frame, 0, receiver))

    # Run the event loop
    event_loop.run(simulation_time=time_limit)

    print(event_loop.current_time)

    # print("Received frames:", receiver.received_frames)
    print('last frame: %d' % receiver.received_frames[-1])
    if receiver.received_frames == sender.frames:
        print('frames matched.')
    else:
        print('frames unmatched.')

    # calculate efficiency
    efficiency = (1 - header_size / frame_size) * len(
        receiver.received_frames) * frame_size / event_loop.current_time / bandwidth / 1e6
    print('experimental efficiency: %f' % efficiency)
    # calculate theoretical efficiency
    theoretical_efficiency = (1 - header_size / frame_size) / (
            1 + ack_size / frame_size + 2 * delay * 1000 * bandwidth / frame_size) * (1 - bit_error_rate) ** (
                                     frame_size + ack_size)
    print('theoretical efficiency: %f' % theoretical_efficiency)