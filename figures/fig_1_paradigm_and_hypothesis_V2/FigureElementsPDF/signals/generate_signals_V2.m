%% low freq signal
f = 0.2;
N = 32;  % number of samples in signal
T = 0:0.1:N-1;
fs = 3;  % sampling rate

LF = sin(2*pi*f*T/fs);
% LF = awgn(LF,20);
plot(LF, 'k', 'LineWidth',2)

%% low freq signal DAMPED
f = 0.2;
N = 32;  % number of samples in signal
T = 0:0.1:N-1;
fs = 3;  % sampling rate

LFD = exp(-T./2).*sin(2*pi*f*T/fs);
% LFD = awgn(LFD,40);
plot(HFD, 'k', 'LineWidth',2)

%% high freq signal
f = 3;
N = 32;  % number of samples in signal
T = 0:0.1:N-1;
fs = 3;  % sampling rate

HF = sin(2*pi*f*T/fs);
% HF = awgn(HF,20);

plot(HF, 'k', 'LineWidth',2)

%% high freq signal DAMPED

f = 3;
N = 32;  % number of samples in signal
T = 0:0.1:N-1;
fs = 3;  % sampling rate

HFD = exp(-T./2).*sin(2*pi*f*T/fs);
% HFD = awgn(HFD,35);

plot(HFD, 'k', 'LineWidth',2)

%%

rng(124)

snr = 100;

% latOCC -> PFt intact
subplot(2,2,1)
I_latOCC_PFt = awgn(HFD, snr);  % snr = 25
plot(I_latOCC_PFt, 'm', 'LineWidth',1); xlim([0,320]); axis off
title('latOCC -> PFt intact')


% PFt <- BA44 intact
subplot(2,2,2)
I_BA44_PFt = awgn(LF + 0.2.*HFD, snr);  % snr = 25
plot(I_BA44_PFt, 'b', 'LineWidth',1); xlim([0,320]); axis off
title('PFt <- BA44 intact')


% latOCC -> PFt scrambled
subplot(2,2,3)
S_latOCC_PFt = awgn(HF, snr);  % snr = 15
plot(S_latOCC_PFt, 'm', 'LineWidth',1); xlim([0,320]); axis off
title('latOCC -> PFt scrambled')


% PFt <- BA44 intact
subplot(2,2,4)
BA44_PFt = awgn(LFD + 0.2.*HFD, snr);  % snr = 40
plot(BA44_PFt, 'b', 'LineWidth',1); xlim([0,320]); axis off
title('PFt <- BA44 intact')


















