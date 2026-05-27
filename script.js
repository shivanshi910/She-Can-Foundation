document.addEventListener('DOMContentLoaded', function(){
  const form = document.getElementById('contactForm');
  const msg = document.getElementById('formMessage');
  const clearBtn = document.getElementById('clearBtn');
  const themeToggle = document.getElementById('themeToggle');

  // Form submit handler: validate client-side and POST to backend API
  form.addEventListener('submit', function(e){
    e.preventDefault();
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const message = document.getElementById('message').value.trim();

    // simple client-side rules
    const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if(name.length < 2){ msg.textContent = 'Name must be at least 2 characters.'; msg.classList.add('error'); return }
    if(!emailRe.test(email)){ msg.textContent = 'Please enter a valid email.'; msg.classList.add('error'); return }
    if(message.length < 10){ msg.textContent = 'Message must be at least 10 characters.'; msg.classList.add('error'); return }

    msg.classList.remove('error');
    const submitBtn = form.querySelector('button[type="submit"]');
    submitBtn.disabled = true;

    fetch('http://localhost:5501/api/contact', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({name, email, message})
    }).then(r=>r.json())
      .then(data=>{
        if(data.ok){
          msg.textContent = data.message || 'Form Submitted Successfully';
          msg.classList.remove('error');
          form.reset();
        } else {
          msg.textContent = data.error || 'Submission failed';
          msg.classList.add('error');
        }
      }).catch(err=>{
        msg.textContent = 'Unable to contact server. Is the backend running?';
        msg.classList.add('error');
      }).finally(()=>{ submitBtn.disabled = false });
  });

  clearBtn.addEventListener('click', function(){
    form.reset();
    msg.textContent = '';
  });

  // Theme toggle: toggles dark variables by toggling class on :root
  themeToggle.addEventListener('click', () => {
    const root = document.documentElement;
    if(root.classList.contains('dark')){
      root.classList.remove('dark');
      themeToggle.textContent = '🌙';
    } else {
      root.classList.add('dark');
      themeToggle.textContent = '☀️';
    }
  });
});
