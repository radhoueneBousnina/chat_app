// document.addEventListener('DOMContentLoaded', function() {
//     document.getElementById('login-form').addEventListener('submit', function(event) {
//         event.preventDefault();
//         const email = document.getElementById('email').value;
//         const password = document.getElementById('password').value;
//
//         fetch('api/v1/dj-rest-auth/login/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': getCookie('csrftoken')
//             },
//             body: JSON.stringify({ email, password })
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (data.key) {
//                 localStorage.setItem('token', data.key);
//                 document.getElementById('login-message').innerText = 'Login successful!';
//             } else {
//                 document.getElementById('login-message').innerText = 'Login failed!';
//             }
//         });
//     });
// });
document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('http://localhost:8000/api/v1/dj-rest-auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')  // Include CSRF token
            },
            body: JSON.stringify({ username, password })
        });
        console.log("yess");
        const data = await response.json();


        if (response.ok) {
            localStorage.setItem('token', data.key);  // Store the token
            document.getElementById('login-message').textContent = 'Login successful!';

            // Redirect to a protected page
            window.location.href = '/api/v1/'

        } else {
            document.getElementById('login-message').textContent = data.non_field_errors || 'Login failed!';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('login-message').textContent = 'An error occurred!';
    }
});
