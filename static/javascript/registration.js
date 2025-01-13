
document.addEventListener('DOMContentLoaded', function() {
    console.log('Registration JavaScript loaded successfully!');
    var form = document.getElementById("registration-form");

    
    form.addEventListener("submit", function(event) {
        event.preventDefault(); 
        
        document.querySelectorAll(".error-message").forEach(function(el) {
            el.textContent = "";
        });

        // Gather form data
        const firstname = document.getElementById('firstname-input-field').value.trim();
        const lastname = document.getElementById('lastname-input-field').value.trim();
        const email = document.getElementById('email-input-field').value.trim();
        const password = document.getElementById('password-input-field').value.trim();
        const cPassword = document.getElementById('confirm-password-input-field').value.trim();

         if (firstname === undefined || lastname === undefined || email === undefined || password === undefined) {
        console.log('One of the fields is undefined');
         }
        var isValid = true;

       
        if (!/^[a-zA-Z0-9_]{3,20}$/.test(firstname)) {
            var fnameError = document.getElementById("firstname-error");
            if (fnameError) {
                fnameError.textContent = "Firstname must be 3-20 characters long and contain only letters";
            }
            isValid = false;
        }

         if (!/^[a-zA-Z0-9_]{3,20}$/.test(lastname)) {
            var lnameError = document.getElementById("lastname-error");
            if (lnameError) {
                lnameError.textContent = "Lastname must be 3-20 characters long and contain only letters";
            }
            isValid = false;
        }

    
        if (!/^[\w\.-]+@[\w\.-]+\.\w+$/.test(email)) {
            var emailError = document.getElementById("email-error");
            if (emailError) {
                emailError.textContent = "Invalid email address";
            }
            isValid = false;
        }

      
        if (password.length < 6) {
            var passwordError = document.getElementById("password-error");
            if (passwordError) {
                passwordError.textContent = "Please enter password (at least 6 characters)";
            }
            isValid = false;
        }

        if(password !== cPassword){

             var cPasswordError = document.getElementById("confirm-password-error");
             if(cPassword){
                cPasswordError.textContent = "Passwords do not match.";
             }
             isValid = false;
        }

        if (!isValid) {
            return; 
        }

        form.submit();
    });
});