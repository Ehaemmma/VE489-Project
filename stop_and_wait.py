import heapq
import random


class Sender:
    def __init__(self, bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop):
        self.bandwidth = bandwidth
        self.delay = delay
        self.bit_error_rate = bit_error_rate
        self.frame_size = frame_size
        self.ack_size = ack_size
        self.frame_error_rate = 1 - (1 - bit_error_rate) ** frame_size
        self.ack_error_rate = 1 - (1 - bit_error_rate) ** ack_size
        self.frames = []
        self.frame_counter = 0  # first un-ACKed frame number
        self.event_loop = event_loop
        self.transmitting = False
        self.transmission_flag = False

    def generate_all_frames(self, num_frames):
        # Add frame sequence number to bit 0
        self.frames = [(i << 1) | (i & 1) for i in range(num_frames)]

    def finish_transmission(self, receiver):
        self.transmitting = False
        if self.transmission_flag:
            self.transmission_flag = False
            self.send_frame(receiver)

    def send_frame(self, receiver):
        if self.frame_counter < len(self.frames):
            frame = self.frames[0]
            transmission_time = self.frame_size / (self.bandwidth * 1e6)
            propagation_time = self.delay / 1000
            total_time = transmission_time + propagation_time
            timeout = 2 * total_time

            print('send %d %d' % (self.frame_counter, frame))
            if random.random() > self.frame_error_rate:
                print('frame %d sent.' % self.frame_counter)
                self.event_loop.add_event(
                    Event(receiver.receive_frame, event_loop.current_time + total_time, frame, self))
            else:
                print('frame %d error.' % self.frame_counter)
            self.event_loop.add_event(
                Event(self.handle_timeout, event_loop.current_time + timeout, receiver, self.frame_counter))

            self.transmitting = True

            self.event_loop.add_event(
                Event(self.finish_transmission, event_loop.current_time + transmission_time, receiver)
            )

    def handle_ack(self, receiver, ack):
        if random.random() > self.ack_error_rate:
            if ack == self.frame_counter ^ 1:
                print('frame %d acked.' % self.frame_counter)
                self.frame_counter ^= 1
                self.frames = self.frames[1:]
                if not self.transmitting:
                    self.send_frame(receiver)
                else:
                    self.transmission_flag = True

    def handle_timeout(self, receiver, timeout_frame_number):
        if self.frame_counter == timeout_frame_number:
            print('resend %d' % self.frame_counter)
            if not self.transmitting:
                self.send_frame(receiver)
            else:
                self.transmission_flag = True


class Receiver:
    def __init__(self, bandwidth, delay, bit_error_rate, ack_size, event_loop):
        self.bandwidth = bandwidth
        self.delay = delay
        self.bit_error_rate = bit_error_rate
        self.ack_size = ack_size
        self.ack_error_rate = 1 - (1 - bit_error_rate) ** ack_size
        self.received_frames = []
        self.expected_frame = 0
        self.event_loop = event_loop

    def receive_frame(self, frame, sender):
        if (frame & 1) == self.expected_frame:
            self.received_frames.append(frame >> 1)
            self.expected_frame ^= 1
        self.send_ack(sender)

    def send_ack(self, sender):
        transmission_time = self.ack_size / (self.bandwidth * 1e6)
        propagation_time = self.delay / 1000
        total_time = transmission_time + propagation_time
        self.event_loop.add_event(
            Event(sender.handle_ack, event_loop.current_time + total_time, self, self.expected_frame))


class Event:
    def __init__(self, handler, timestamp, *args):
        self.handler = handler
        self.timestamp = timestamp
        self.args = args

    def __lt__(self, other):
        return self.timestamp < other.timestamp

    def __str__(self):
        return "% .1f\n" % (self.timestamp*1000) + self.handler.__name__


class EventLoop:
    def __init__(self):
        self.event_queue = []
        self.current_time = 0

    def run(self, simulation_time=1e8):
        while self.event_queue and self.current_time < simulation_time:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.timestamp
            print(event)
            event.handler(*event.args)

    def add_event(self, event):
        heapq.heappush(self.event_queue, event)


if __name__ == "__main__":
    time_limit = 1 * 60  # seconds

    bandwidth = 1  # Mbps
    delay = 100  # ms
    bit_error_rate = 1e-5
    frame_size = 1250 * 8 # bits
    ack_size = 25 * 8  # bits
    header_size = 25 * 8  # bit
    num_frames = 1000000

    event_loop = EventLoop()
    sender = Sender(bandwidth, delay, bit_error_rate, frame_size, ack_size, event_loop)
    receiver = Receiver(bandwidth, delay, bit_error_rate, ack_size, event_loop)

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
    efficiency = (1 - header_size / frame_size) * len(receiver.received_frames) * frame_size / event_loop.current_time / bandwidth / 1e6
    print('experimental efficiency: %f' % efficiency)
    # calculate theoretical efficiency
    theoretical_efficiency = (1 - header_size / frame_size) / (1 + ack_size / frame_size + 2 * delay * 1000 * bandwidth / frame_size) * (1 - bit_error_rate) ** (frame_size + ack_size)
    print('theoretical efficiency: %f' % theoretical_efficiency)
