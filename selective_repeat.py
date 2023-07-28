from stop_and_wait import Sender, Receiver, Event, EventLoop
from go_back_N import GBN_Sender, GBN_Receiver
import numpy as np
import random


class SR_Sender(GBN_Sender):
    def __init__(self, bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop, window_size):
        super().__init__(bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop, window_size)

    def send_frame(self, receiver):
        frame = -1
        # check whether resend is need
        if RESEND_QUEUE_IS_NOT_EMPTY:
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
    pass
