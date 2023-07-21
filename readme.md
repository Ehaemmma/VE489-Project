# VE489 - Project

## Zhenxuan Su, Sen Wang, Yuchen Zhou

This project is to implement three ARQ protocols, i.e., stop‐and‐wait, go‐back‐N, and 
selective‐repeat in Python. The realization of each protocol is in the corresponding branch.

- Stop-and-Wait
- Go-Back-N
- Selective-Repeat

### Main

In ```main.py```, we implement the sender and receiver, the event loop and the main function.

#### Sender and Receiver

The important attributes of sender and receiver include bandwidth, delay, frame size, ack size, a list to store and compare the received frames. To detect the efficiency and accuracy, there are frame error rate, act error rate and frame counter.

##### Sender

Sender sends a frame to the receiver, with total transmission time and frame counter calculated. The function triggers receiver to receive and the transmitting status will be set to true until the frame is transmitted (triggering finish_transmission event). If timeout or wrong ack info is detected, the sender would trigger functions to resend the frame.

##### Receiver

The `Receiver` class represents a data receiver in a network. It can receive frames from the sender and send acknowledgments back.

#### Event

The `Event` class models an event that occurs at a certain timestamp with associated arguments.

##### Event Loop

The `EventLoop` class is a simulation of an event-based programming model. It keeps track of all events and runs them in chronological order.
