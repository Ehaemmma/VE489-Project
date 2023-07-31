# VE489 - Project

## Zhenxuan Su, Sen Wang, Yuchen Zhou

This project is to implement three ARQ protocols, i.e., stop‐and‐wait, go‐back‐N, and 
selective‐repeat in Python. The realization of each protocol is in the corresponding python files.

- [Stop-and-Wait](https://github.com/Ehaemmma/VE489-Project/blob/main/stop_and_wait.py)
- [Go-Back-N](https://github.com/Ehaemmma/VE489-Project/blob/main/go_back_N.py)
- [Selective-Repeat](https://github.com/Ehaemmma/VE489-Project/blob/main/selective_repeat.py)

#### Sender and Receiver

The important attributes of sender and receiver include bandwidth, delay, frame size, ack size, a list to store and compare the received frames. To detect the efficiency and accuracy, there are frame error rate, act error rate and frame counter.

##### Sender

Sender sends a frame to the receiver, with total transmission time and frame counter calculated. The function triggers receiver to receive and the transmitting status will be set to true until the frame is transmitted (triggering finish_transmission event). If timeout or wrong ack info is detected, the sender would trigger functions to resend the frame.

##### Receiver

The `Receiver` class represents a data receiver in a network. It can receive frames from the sender and send acknowledgments back.

#### Stop & Wait Events

1. **Generate All Frames**: This event is triggered at the beginning of the simulation to generate all the frames that the sender will send to the receiver.
2. **Send Frame**: This event is triggered when the sender sends a frame to the receiver. The sender calculates the total time it takes for the frame to be transmitted and received, and adds a `receive_frame` event to the event loop with the appropriate timestamp. It also adds a `handle_timeout` event to the event loop.
3. **Receive Frame**: This event is triggered when the receiver receives a frame from the sender. The receiver checks if the frame is the expected frame, and if so, appends it to the list of received frames and updates the expected frame number. The receiver then sends an acknowledgment (ACK) back to the sender by triggering a `send_ack` event.
4. **Send ACK**: This event is triggered when the receiver sends an ACK back to the sender. The receiver calculates the total time it takes for the ACK to be transmitted and received, and adds a `handle_ack` event to the event loop with the appropriate timestamp.
5. **Handle ACK**: This event is triggered when the sender receives an ACK from the receiver. If the ACK is for the current frame, the sender increments the frame counter and sends the next frame if there are more frames to send, otherwise it resend current frame.
6. **Handle Timeout**: This event is triggered when the sender detects a timeout for the current frame. If the frame counter is still the same as the timeout frame number, the sender resends the frame.
7. **Compare frames**: Compare whether the expected frame is the same as the received frame.
8. **Finish Transmission**: This event is triggered when the sender finished transmitting a frame. If ACK or timeout is triggered during the past transmission, the frame is resent now.

#### Go-Back-N Events

The simulation is based on an event-driven programming approach, where different events are processed by the event loop. The main events in the Go back N ARQ protocol simulation are:

1. **Generate All Frames**: This event is triggered at the beginning of the simulation to generate all the frames that the sender will send to the receiver.
2. **Load frames**: This event load frames to the sending window whenever there is spot (for initialization and refill).
3. **Go back N**: When this event is triggered, the sender goes back N (window size) frames which means resending the last unacked frame and setting the next frame accordingly. 
4. **Send Frame**: This event is triggered when the sender sends a frame to the receiver. The sender calculates the total time it takes for the frame to be transmitted and received, and adds a `receive_frame` event to the event loop with the appropriate timestamp. It also adds a `handle_timeout` event to the event loop.
5. **Receive Frame**: This event is triggered when the receiver receives a frame from the sender. The receiver checks if the frame is the expected frame, and if so, appends it to the list of received frames and updates the expected frame number. The receiver then sends an acknowledgment (ACK) back to the sender by triggering a `send_ack` event.
6. **Send ACK**: This event is triggered when the receiver sends an ACK back to the sender. The receiver calculates the total time it takes for the ACK to be transmitted and received, and adds a `handle_ack` event to the event loop with the appropriate timestamp.
7. **Handle ACK**: This event is triggered when the sender receives an ACK from the receiver. If the ACK is one of the last N unacked frames, the sender increments the frame counter and sends the next frame if there are more frames to send, and if the earliest unacked frame is large or equal to N from the next frame, it triggers go back N.
8. **Handle Timeout**: This event is triggered when the sender detects a timeout for the current frame. If the frame counter is still the same as the timeout frame number, the sender resends the frame.
9. **Compare frames**: Compare whether the expected frame is the same as the received frame.
10. **Finish Transmission**: This event is triggered when the sender finished transmitting a frame. If ACK or timeout is triggered during the past transmission, the frame is resent now.

#### Selective Repeat Events

The simulation is based on an event-driven programming approach, where different events are processed by the event loop. The main events in the Go back N ARQ protocol simulation are:

1. **Generate All Frames**: This event is triggered at the beginning of the simulation to generate all the frames that the sender will send to the receiver.

2. **Load frames**: This event load frames to the sending window whenever there is spot (for initialization and refill).
3. **Send Frame**: This event is triggered when the sender sends a frame to the receiver. The sender calculates the total time it takes for the frame to be transmitted and received, and adds a `receive_frame` event to the event loop with the appropriate timestamp. It also adds a `handle_timeout` event to the event loop.

3. **Receive Frame**: This event is triggered when the receiver receives a frame from the sender. The receiver checks if the frame is one of the expected frame in the receiving window, and if so, it adds it to the list of received frames and updates the expected frame list. The receiver then sends an acknowledgment (ACK) back to the sender by triggering a `send_ack` event.

4. **Send ACK**: This event is triggered when the receiver sends an ACK back to the sender. The receiver calculates the total time it takes for the ACK to be transmitted and received, and adds a `handle_ack` event to the event loop with the appropriate timestamp.

1. **Handle ACK**: This event is triggered when the receiver sends an acknowledgment (ACK) for a received frame. If the ACK number is greater than the latest unacknowledged frame number plus one, it updates the latest unacknowledged frame to the ACK number. If there is an NAK frame pending and its number is less than the latest unacknowledged frame number, the NAK frame is cleared. And if the ACK number is less than the latest unacknowledged frame number, it is considered a negative acknowledgment (NAK), and the corresponding frame needs to be resent. The NAK frame is set, and if there were no frames to send before, it schedules a send_frame event to resend the frame.
2. **Handle Timeout**: This event is triggered when the sender detects a timeout for the current frame. If the frame counter is still the same as the timeout frame number, the sender resends the frame.
3. **Compare frames**: Compare whether the expected frame is the same as the received frame.
4. **Finish Transmission**: This event is triggered when the sender finished transmitting a frame. If ACK or timeout is triggered during the past transmission, the frame is resent now.

#### Running the Simulation

To run the simulation, simply execute the provided Python script. The simulation will run with the specified parameters (bandwidth, delay, bit error rate, frame size, and ACK size) and generate a list of received frames at the receiver. The simulation will also calculate the experimental efficiency and compare it with the theoretical efficiency.
