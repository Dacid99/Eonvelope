document.querySelectorAll('.spinner-text').forEach(button => {
    button.addEventListener('click', function () {
        const textContent = this.querySelector('.spinner-text-content');
        const spinner = this.querySelector('.spinner-border');

        textContent.classList.add('opacity-0');
        spinner.classList.remove('d-none');
    });
});
