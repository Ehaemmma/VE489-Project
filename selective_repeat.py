from stop_and_wait import Sender, Receiver, Event, EventLoop
import numpy as np
import random

class SR_Sender(Sender):
    def __init__(self, bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop, window_size):
        super().__init__(bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop)
        self.window_size = window_size
        self.next_frame = 0
        self.latest_unacked_frame = 0
        self.send_window = [-1 for i in range(self.window_size)]
        self.timeout_flag = False

    def send_frame(self, receiver):
        pass

    def handle_ack(self, receiver, ack):
        if random.random() > self.ack_error_rate:
            if self.send_window[ack] != -1:
                self.send_window[ack] = -1
                self.latest_unacked_frame = max(self.latest_unacked_frame, ack + 1)


class SR_Receiver(Receiver):
    def __init__(self, bandwidth, delay, bit_error_rate, ack_size, event_loop, window_size):
        super().__init__(bandwidth, delay, bit_error_rate, ack_size, event_loop)
        self.window_size = window_size
        self.sequence_number_length = int(np.ceil(np.log2(self.window_size + 1)))
        self.receive_window = [-1 for i in range(self.window_size)]

    def receive_frame(self, frame, sender):
        sequence_number = frame & ((1 << self.sequence_number_length) - 1)
        if self.receive_window[sequence_number] == -1:
            self.receive_window[sequence_number] = frame >> self.sequence_number_length
        self.send_ack(sender, sequence_number)