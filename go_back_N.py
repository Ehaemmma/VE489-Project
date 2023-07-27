import numpy as np
import random
from stop_and_wait import Sender, Receiver, Event, EventLoop, WriteOutput


class GBN_Sender(Sender):
    def __init__(self, bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop, N):
        super().__init__(bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop)
        self.n_o = np.ceil(np.log2(N + 1))
        self.window_size = 1 << self.n_o
        self.next_frame = 0
        self.latest_unacked_frame = 0
        self.send_window = [-1 for i in range(self.window_size)]
        self.timeout_flag = False
    #
    # def unacked(self, frame_number):
    #     return (
    #                 self.latest_acked_frame < frame_number < self.next_frame) if self.next_frame > self.latest_acked_frame else (
    #                 frame_number > self.latest_acked_frame or frame_number < self.next_frame)

    def generate_all_frames(self, num_frames):
        # Add frame sequence number to the rightmost bits
        self.frames = [(i << self.n_o) | (i & ((1 << self.n_o) - 1)) for i in range(num_frames)]

    def finish_transmission(self, receiver):
        # one fransmission is finished, next transmission can be started
        self.transmitting = False
        if self.timeout_flag:
            self.timeout_flag = False
            # Do something

    def load_frames(self):
        window_index = self.next_frame
        while self.send_window[window_index] == -1:
            if len(self.frames) == 0:
                return
            self.window_size[window_index] = self.frames[0]
            self.frames = self.frames[1:]
            window_index = (1 + window_index) % self.window_size

    def go_back_N(self):
        pass

    def send_frame(self, receiver):
        if SOMETHING:
            self.go_back_N()
        if self.send_window[self.next_frame] == -1:
            self.load_frames()
        frame = self.frames[self.next_frame]
        if frame == -1:
            # No frame to send
            return
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

        self.next_frame = (self.next_frame + 1) % self.window_size

    def handle_ack(self, receiver, ack):
        # to be modified
        pass

    def handle_timeout(self, receiver, timeout_frame_number):
        # to be modified
        pass


class GBN_Receiver(Receiver):
    pass

    def receive_frame(self, frame, sender):
        if (frame & 1) == self.expected_frame:
            self.received_frames.append(frame >> 1)
            self.expected_frame ^= 1
        self.send_ack(sender)


if __name__ == "__main__":
    time_limit = 1 * 60  # seconds

    bandwidth = 1  # Mbps
    delay = 100  # ms
    bit_error_rate = 1e-5
    frame_size = 1250 * 8  # bits
    ack_size = 25 * 8  # bits
    header_size = 25 * 8  # bit
    num_frames = 1000000

    event_loop = EventLoop()
    sender = GBN_Sender(bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop)
    receiver = GBN_Receiver(bandwidth, delay, bit_error_rate, ack_size, event_loop)

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

    # write main data into output files
    file = open('output.txt', mode='w', encoding='utf-8')
    file.write('bandwidth: ' + str(bandwidth) + 'Mbps\n')
    file.write('delay: ' + str(delay) + 'ms\n')
    file.write('bit error rate: ' + str(bit_error_rate) + '\n')
    file.write('theoretical efficiency: ' + str(theoretical_efficiency) + '\n')
    file.write('experimental efficiency: ' + str(efficiency) + '\n')
    file.close()
