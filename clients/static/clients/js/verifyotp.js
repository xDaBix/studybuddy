
document.addEventListener('DOMContentLoaded', () => {
    const otpInputs = document.querySelectorAll('.otp-input');
    
    otpInputs.forEach((input, index) => {
        input.addEventListener('input', () => {
            if (input.value.length === 1 && index < otpInputs.length - 1) {
                otpInputs[index + 1].focus();
            }
        });
        
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && input.value.length === 0 && index > 0) {
                otpInputs[index - 1].focus();
            }
        });
    });

    const otpForm = document.getElementById('otpForm');
    otpForm.addEventListener('submit', (e) => {
        e.preventDefault();

        const otp = Array.from(otpInputs).map(input => input.value).join('');
        const hiddenOtpInput = document.createElement('input');
        hiddenOtpInput.type = 'hidden';
        hiddenOtpInput.name = 'otp';
        hiddenOtpInput.value = otp;

        otpForm.appendChild(hiddenOtpInput);
        otpForm.submit();
    });
});