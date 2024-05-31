document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('register-form').addEventListener('submit', function(event) {
        event.preventDefault();
        const first_name = document.getElementById('first_name').value;
        const last_name = document.getElementById('last_name').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        fetch('http://0.0.0.0:8000/api/v1/dj-rest-auth/registration/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ first_name, last_name, email, password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.key) {
                localStorage.setItem('token', data.key);
                document.getElementById('register-message').innerText = 'Registration successful!';
            } else {
                document.getElementById('register-message').innerText = 'Registration failed!';
            }
        });
    });
});
