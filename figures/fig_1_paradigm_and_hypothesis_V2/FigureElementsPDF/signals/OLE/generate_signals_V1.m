%% low freq signal

f = 0.05;
N = 200;  % number of samples in signal
fs = 3;  % sampling rate

x = sin(2*pi*f*(0:N-1)/fs);
x = awgn(x,10);

plot(x,'b', 'LineWidth',2)
print('signal_low_freq','-dsvg')


%% mid freq signal

f = 0.1;
N = 200;  % number of samples in signal
fs = 3;  % sampling rate

x = sin(2*pi*f*(0:N-1)/fs);
x = awgn(x,10);

plot(x, 'r', 'LineWidth',2)
print('signal_mid_freq','-dsvg')


%% high freq signal DAMPED

f = 0.5;
N = 200;  % number of samples in signal
fs = 3;  % sampling rate

T = 0:N-1;

x = sin(2*pi*f*T/fs);

x = awgn(x,10);


plot(x, 'k', 'LineWidth',2)
print('signal_high_freq','-dsvg')




%% high freq signal DAMPED

f = 0.5;
N = 200;  % number of samples in signal
fs = 3;  % sampling rate

T = 0:N-1;

x = exp(-T./20).*sin(2*pi*f*T/fs);

x = awgn(x,30);


plot(x, 'k', 'LineWidth',2)
print('signal_high_freq','-dsvg')


