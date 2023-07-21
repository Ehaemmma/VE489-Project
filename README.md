### Stop and Wait ARQ Protocol Simulation

This Python code simulates the Stop and Wait Automatic Repeat Request (ARQ) protocol, which is a simple flow control method used in telecommunications to ensure reliable and ordered delivery of data frames.

#### Events
The simulation is based on an event-driven programming approach, where different events are processed by the event loop. The main events in the Stop and Wait ARQ protocol simulation are:1. **Generate All Frames**: This event is triggered at the beginning of the simulation to generate all the frames that the sender will send to the receiver.

1. **Send Frame**: This event is triggered when the sender sends a frame to the receiver. The sender calculates the total time it takes for the frame to be transmitted and received, and adds a `receive_frame` event to the event loop with the appropriate timestamp. It also adds a `handle_timeout` event to the event loop.
2. **Receive Frame**: This event is triggered when the receiver receives a frame from the sender. The receiver checks if the frame is the expected frame, and if so, appends it to the list of received frames and updates the expected frame number. The receiver then sends an acknowledgment (ACK) back to the sender by triggering a `send_ack` event.
3. **Send ACK**: This event is triggered when the receiver sends an ACK back to the sender. The receiver calculates the total time it takes for the ACK to be transmitted and received, and adds a `handle_ack` event to the event loop with the appropriate timestamp.
4. **Handle ACK**: This event is triggered when the sender receives an ACK from the receiver. If the ACK is for the current frame, the sender increments the frame counter and sends the next frame if there are more frames to send, otherwise it resend current frame.
5. **Handle Timeout**: This event is triggered when the sender detects a timeout for the current frame. If the frame counter is still the same as the timeout frame number, the sender resends the frame.
6. **Finish Transmission**: This event is triggered when the sender finished transmitting a frame. If ACK or timeout is triggered during the past transmission, the frame is resent now.

#### Running the Simulation

To run the simulation, simply execute the provided Python script. The simulation will run with the specified parameters (bandwidth, delay, bit error rate, frame size, and ACK size) and generate a list of received frames at the receiver. The simulation will also calculate the experimental efficiency and compare it with the theoretical efficiency.
