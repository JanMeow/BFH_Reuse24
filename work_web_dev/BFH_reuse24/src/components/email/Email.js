import React from 'react';
import { useState, useRef } from 'react';
import emailjs from '@emailjs/browser';



const Contact = () => {

  const [templateId, serviceId,publickKey] = ['template_iwhs6pa', 'service_g29h0gb', '468L19xUKeyORsiDq']


  const  defaultFormState = 
  {
    name:'',
    email:'',
    message:''
  }

  const formRef = useRef();
  const [form, setForm] = useState(defaultFormState);
  const [loading, setLoading] = useState(false);


  const handleChange = (event) =>{
    const {name, value} = event.target;
    setForm({...form, [name]: value})
  };

  const handleSubmit = (event) =>{
    event.preventDefault();
    setLoading(true);

    emailjs.send(
      serviceId,
      templateId,
      {
        from_name: form.name,
        to_name: 'Jan',
        from_email: form.email,
        to_email: 'lawmankiian@gmail.com',
        message: form.message
      },
      publickKey)
      .then(()=>{
        setLoading(false);
        alert('Thank you for your message, I will get back to you soon !')
        setForm(defaultFormState)
      }).catch((err)=>{
        setLoading(false);
        alert('Something went wrong')
      })
  };


  return (
    <div className='xl:mt-12 xl:flex-row flex-col-reverse flex gap-10 overflow-hidden'>
        <p className= {styles.sectionSubText}>Get in touch</p>
        <h3 className= {styles.sectionHeadText}>Contact</h3>
        <form
          ref = {formRef}
          onSubmit={handleSubmit}
          className='mt-12 flex flex-col gap-8'
        >
          <label className='flex flex-col'>
            <span className='text-white underline font-medium mb-4 text-left'>Your Name</span>
            <input 
              type = 'text'
              name = 'name'
              value = {form.name}
              onChange = {handleChange}
              placeholder='Enter Your Name'
              className='bg-tertiary py-4 px-6 placeholder:text-secondary placeholder:text-xs text-white rounded-lg outlined-none border-none font-medium'
            >
            </input>
          </label>
          <label className='flex flex-col'>
              <span className='text-left underline text-white font-medium mb-4'>Your Email</span>
            <input 
              type = 'email'
              name = 'email'
              value = {form.email}
              onChange = {handleChange}
              placeholder='Enter Your email'
              className='bg-tertiary py-4 px-6 placeholder:text-secondary placeholder:text-xs text-white rounded-lg outlined-none border-none font-medium'
            >
            </input>
          </label>
            <label className='flex flex-col'>
              <span className='text-left underline text-white font-medium mb-4 '>Your Message</span>
              <input 
                rows = '7'
                name = 'message'
                value = {form.message}
                onChange = {handleChange}
                placeholder='What is your message'
                className='bg-tertiary py-4 px-6 placeholder:text-secondary placeholder:text-xs text-white rounded-lg outlined-none border-none font-medium'
              >
              </input>
            </label>
            <button
              type = 'submit'
              className='bg-tertiary py-3 px-8 border hover:scale-110 hover:border-2 w-fit text-white font-bold shadow-md shadow-primary rounded-xl'
            >
              {loading? 'Sending...':'Send'}
            </button>
        </form>
    </div>
  )
}

export default Contact