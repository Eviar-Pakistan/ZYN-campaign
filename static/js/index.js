function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');
  



// ================================ Signup Functionality ============================================//
const signupForm = document.getElementById("signupForm");
const signupbtn = document.getElementById("signupbtn");
const otpSection = document.getElementById("otpSection");
const verifyOtpBtn = document.getElementById("verifyOtpBtn");

let otpGenerated = null;  // To store the generated OTP for verification

signupbtn && signupbtn.addEventListener("click", (e) => {
    e.preventDefault();
    const fname = document.getElementById('fname').value.trim();
    const lname = document.getElementById('lname').value.trim();
    const contactNo = document.getElementById('contactNo').value.trim();
    const signuppassword = document.getElementById('password').value.trim();
    const rewardCode = document.getElementById('rewardCode').value.trim();
    const checkbox1 = document.getElementById('checkbox1').checked;

    let isValid = true;
    const nameRegex = /^[A-Za-z]+$/;
    const contactRegex = /^[0-9]{11}$/;
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$/;
    const rewardRegex = /^SR06-\w{5}$/;

    if (!nameRegex.test(fname) || !nameRegex.test(lname)) {
        alert("First and Last name should only contain alphabets.");
        isValid = false;
    } else if (!contactRegex.test(contactNo)) {
        alert("Contact number should be 11 digits.");
        isValid = false;
    } else if (!passwordRegex.test(signuppassword)) {
        alert("Password must be at least 6 characters long and include both letters and numbers.");
        isValid = false;
    } else if (!rewardRegex.test(rewardCode)) {
        alert("Invalid or already used reward code.");
        isValid = false;
    } else if (!checkbox1) {
        alert("You must agree to the Terms and Conditions.");
        isValid = false;
    }

    if (isValid) {
      fetch('send-otp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ contactNo: contactNo })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("OTP sent successfully!");
            // otpGenerated = data.otp; 
            // document.getElementById("otpSection").style.display = "block";
            // document.getElementById("signupbtn").style.display = "none"
            // console.log(data)
            const fname = document.getElementById('fname').value.trim();
          const lname = document.getElementById('lname').value.trim();
          const signuppassword = document.getElementById('password').value.trim();
          const rewardCode = document.getElementById('rewardCode').value.trim();

          const formData = {
              fname: fname,
              lname: lname,
              contactNo: contactNo,
              signuppassword: signuppassword,
              rewardCode: rewardCode,
          };

          // Send signup request
          fetch('signup', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json',
                  'X-CSRFToken': csrftoken,
              },
              body: JSON.stringify(formData),
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  alert("Signup successful!");
                  window.location.href = "signin";
              } else {
                  alert("Something went wrong: " + data.message);
              }
          })
          .catch(error => {
              alert("An error occurred during signup: " + error.message);
          });
        } else {
            alert("Failed to send OTP: " + data.message);
        }
    })
    .catch(error => {
        alert("Error sending OTP: " + error.message);
    });
    }
});


// verifyOtpBtn && verifyOtpBtn.addEventListener("click", (e) => {
//   e.preventDefault();

//   const otpInput = document.getElementById('otp').value.trim();
//   const contactNo = document.getElementById("contactNo").value.trim();
//   console.log(otpInput, contactNo)

//   // Send OTP verification request
//   fetch('verify-otp', {
//       method: 'POST',
//       headers: {
//           'Content-Type': 'application/json',
//           'X-CSRFToken': csrftoken2,
//       },
//       body: JSON.stringify({ contactNo: contactNo, otpInput: otpInput })
//   })
//   .then(response => response.json())
//   .then(data => {
//       if (data.success) {
//           alert("OTP verified successfully!");
          // OTP is verified, proceed with signup
          
//       } else {
//           alert("Invalid OTP: " + data.message);
//       }
//   })
//   .catch(error => {
//       alert("Error verifying OTP: " + error.message);
//   });
// });



    // ================================ Signup Functionality ============================================//


    // ================================ SignIn Functionality ============================================//

    const signinForm = document.getElementById("signinForm")
    const signinbtn = document.getElementById("signinbtn")

    signinbtn && signinbtn.addEventListener("click",(e)=>{
        e.preventDefault()
        const signinContact = document.getElementById("contactNo").value.trim()
        const signinPassword = document.getElementById("password").value.trim()


        const signinData = {
            contactNo:signinContact,
            password:signinPassword
        }

        fetch("signin",{
            method:"POST",
            headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
            },
            body: JSON.stringify(signinData)
        
                })
                .then(response => response.json())
                .then(data => {
                  if (data.success) {
                    alert("Signin successful!");
                    signinForm.reset(); 
                    window.location.href = data.redirect; 

                  } else {
                    alert("Something went wrong: " + data.message);
                  }
                })
                .catch(error => {
                  alert("An error occurred: " + error.message);
                });
            
    })

    // ================================ SignIn Functionality ============================================//

// ====================================Email Verification Functioanlity ============================================//

const emailBtn = document.getElementById('emailTakingForm')

emailBtn && emailBtn.addEventListener('submit', function(event) {
  event.preventDefault();
  const email = document.getElementById('email').value;

  fetch('emailTaking', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ email: email })
  }).then(response => response.json()).then(data => {
      if (data.success) {
          window.location.href = data.redirect;
      } else {
          alert(data.message);
      }
  });
});

const emailverify = document.getElementById('emailVerificationForm')

emailverify && emailverify.addEventListener('submit', function(event) {
  event.preventDefault();

  fetch('emailVerification', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
      }
  }).then(response => response.json()).then(data => {
      if (data.success) {
          alert(data.message);
      } else {
          alert('Error sending email.');
      }
  });
});


// ====================================Email Verification Functioanlity ============================================//



    // ================================ Points Accumulated Functionality ================================//

    const addPoints =  document.getElementById("pointBtn")

      addPoints && addPoints.addEventListener("click", function () {
      const rewardCodeInput = document.getElementById("rewardCode").value.trim(); 
      const pointsBar = document.getElementById("pointsBar");
      const pointsStatus = document.getElementById("pointsStatus");
      const surveyPoints = document.getElementById("surveyPoints");
      const completeSurvey = document.getElementById("completeSurvey")
  
      fetch("/rewardCodes", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": csrftoken,
          },
          body: JSON.stringify({ rewardCode: rewardCodeInput }),
      })
          .then((response) => response.json())
          .then((data) => {
              if (data.success) {
                  const updatedPoints = data.pointsAccumulated;
                  pointsBar.value = updatedPoints;
                  pointsStatus.innerText = `${updatedPoints}/800`;
                  surveyPoints.innerText = `${updatedPoints}/160`
                  alert("You have got a points successfully!");

                  if(updatedPoints == 160){
                    completeSurvey.disabled = false
                  }

              } else {
                  alert(data.message || "Invalid reward code or already used.");
              }
          })
          .catch((error) => {
              console.error("Error:", error);
              alert("An error occurred while processing your request.");
          });
  });
  

    







    // ================================ Points Accumulated Functionality ================================//
