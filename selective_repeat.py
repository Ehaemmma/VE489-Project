from stop_and_wait import Sender, Receiver, Event, EventLoop
from go_back_N import GBN_Sender, GBN_Receiver
import numpy as np
import random


class SR_Sender(Sender):
    def __init__(self, bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop, window_size):
        super().__init__(bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop)
        self.window_size = window_size
        self.latest_unacked_frame = 0
        self.next_frame = 0
        self.frames_numbers = 0
        self.nak_frame = -1
        self.flag_no_frames = False
        self.n_o = int(np.ceil(np.log2(2 * window_size + 1)))

    def generate_all_frames(self, num_frames):
        # Add frame sequence number to bit 0
        # One bit frame sequence number for stop and wait
        self.frames = [i for i in range(num_frames)]
        self.frames_numbers = num_frames
        self.frames_copy = self.frames.copy()

    def compare_frames(self, received_frames):
        return self.frames_copy == received_frames

    def finish_transmission(self, receiver):
        # one fransmission is finished, next transmission can be started
        self.transmitting = False
        self.send_frame(receiver)

    def send_frame(self, receiver):
        frame = -1

        transmission_time = self.frame_size / (self.bandwidth * 1e6)
        propagation_time = self.delay / 1000
        total_time = transmission_time + propagation_time
        timeout = 2 * total_time

        if not self.nak_frame == -1:
            frame = self.nak_frame
            self.nak_frame = -1
            print('resend frame %d.' % frame)
        else:
            if self.next_frame - self.latest_unacked_frame >= self.window_size:
                self.next_frame -= 1
                frame = self.next_frame
            else:
                frame = self.next_frame
                if frame >= self.frames_numbers:
                    frame = -1
            if frame == -1:
                # No frame to send
                print('no frames to send.')
                self.flag_no_frames = True
                self.event_loop.add_event(
                    Event(self.handle_timeout, event_loop.current_time + timeout, receiver, self.next_frame))

                return

            print('send %d %d' % (self.next_frame & ((1 << self.n_o) - 1), frame))
            self.next_frame += 1
        if random.random() >= self.frame_error_rate:
            print('frame %d sent.' % frame)
            self.event_loop.add_event(
                Event(receiver.receive_frame, event_loop.current_time + total_time, frame, self))

        # self.event_loop.add_event(
        #     Event(self.handle_timeout, event_loop.current_time + timeout, receiver, self.next_frame))
        self.transmitting = True

        self.event_loop.add_event(
            Event(self.finish_transmission, event_loop.current_time + transmission_time, receiver)
        )

    def handle_ack(self, receiver, ack):
        if random.random() >= self.ack_error_rate:  # successfully receive ack
            if ack >= self.latest_unacked_frame + 1:
                print('frame ' + str(self.latest_unacked_frame) + ' acked.')
                self.latest_unacked_frame = ack
                if self.nak_frame < self.latest_unacked_frame:
                    self.nak_frame = -1
                # if ack - 1 in self.frames:
                #     self.frames.remove(ack - 1)
                # else:
                #     self.transmission_flag = True
                # self.next_frame = ack
            else:
                if ack == self.next_frame:
                    return
                print('latest unack: %d.' % self.latest_unacked_frame)
                print('frame ' + str(ack) + ' naked.')
                self.nak_frame = ack
                if self.flag_no_frames:
                    self.flag_no_frames = False
                    self.send_frame(receiver)
        else:
            # ack transmission fail
            print('ack %d lost.' % ack)

    def handle_timeout(self, receiver, timeout_frame_number):
        # resend when timeout
        if self.flag_no_frames and not self.latest_unacked_frame == self.next_frame:
            print(self.latest_unacked_frame, self.next_frame)
            self.flag_no_frames = False
            self.next_frame -= 1
            self.send_frame(receiver)


class SR_Receiver(Receiver):
    def __init__(self, bandwidth, delay, bit_error_rate, ack_size, event_loop, window_size):
        super().__init__(bandwidth, delay, bit_error_rate, ack_size, event_loop)
        self.window_size = window_size
        self.unreceived_frames = []

    def receive_frame(self, frame, sender):
        # extract the one bit frame sequence number and compare to the expected frame number
        if frame == self.expected_frame:
            # if frame in self.unreceived_frames:
            #     self.unreceived_frames.remove(frame)
            self.received_frames.append(frame)
            self.expected_frame += 1
            while len(self.unreceived_frames) > 0 and self.unreceived_frames[0] == self.expected_frame:
                self.received_frames.append(self.unreceived_frames[0])
                self.expected_frame += 1
                self.unreceived_frames.pop(0)
            #
            # if len(self.unreceived_frames) == 0:
            #     self.expected_frame = len(self.received_frames)
            # else:
            #     self.unreceived_frames.sort()  # Maybe not necessary
            #     self.expected_frame = self.unreceived_frames[0]
            self.send_ack(sender)
        else:
            if self.expected_frame < frame < self.expected_frame + self.window_size:
                if len(self.unreceived_frames) == 0 or not frame == self.unreceived_frames[-1]:
                    self.unreceived_frames.append(frame)
            # for i in range(self.expected_frame, frame):
            #     if i not in self.received_frames:
            #         self.unreceived_frames.append(i)
            self.send_ack(sender)
        print('frame %d received.' % frame)
        # print(self.received_frames)
        # print(self.unreceived_frames)

    def send_ack(self, sender):
        transmission_time = self.ack_size / (self.bandwidth * 1e6)
        propagation_time = self.delay / 1000
        total_time = transmission_time + propagation_time
        self.event_loop.add_event(
            Event(sender.handle_ack, self.event_loop.current_time + total_time, self, self.expected_frame))


if __name__ == "__main__":
    time_limit = 1 * 60  # seconds

    bandwidth = 1  # Mbps
    delay = 10  # ms
    bit_error_rate = 1e-5
    frame_size = 1250 * 8  # bits
    ack_size = 25 * 8  # bits
    header_size = 25 * 8  # bit
    num_frames = 1000000
    window_size = 10
    frame_error_rate = 1 - (1 - bit_error_rate) ** (frame_size)

    event_loop = EventLoop()
    sender = SR_Sender(bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop, window_size)
    receiver = SR_Receiver(bandwidth, delay, bit_error_rate, ack_size, event_loop, window_size)

    # Add the initial event to generate all frames
    sender.generate_all_frames(num_frames)
    event_loop.add_event(Event(sender.send_frame, 0, receiver))

    # Run the event loop
    event_loop.run(simulation_time=time_limit)

    print(event_loop.current_time)

    # print("Received frames:", receiver.received_frames)
    print('last frame: %d' % receiver.received_frames[-1])
    if sender.compare_frames(receiver.received_frames):
        print('frames matched.')
    else:
        # print('received:')
        # print(receiver.received_frames)
        print('frames unmatched.')

    # calculate efficiency
    efficiency = (1 - header_size / frame_size) * len(
        receiver.received_frames) * frame_size / event_loop.current_time / bandwidth / 1e6
    print('experimental efficiency: %f' % efficiency)
    # calculate theoretical efficiency
    theoretical_efficiency = (1 - header_size / frame_size) * (1 - bit_error_rate) ** (
        frame_size)
    print('theoretical efficiency: %f' % theoretical_efficiency)
