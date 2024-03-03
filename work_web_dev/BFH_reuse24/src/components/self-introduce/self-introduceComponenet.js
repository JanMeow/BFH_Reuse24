import './self-introductionStyle.scss';
import Button from '../button/buttonComponent';
import { useRef } from 'react';

const Introduction = ({targetElementRef}) =>{


    const scrollToElement = () =>{ 


        if (targetElementRef.current) {
            const offset = 140; // Offset from the target element
            const bodyRect = document.body.getBoundingClientRect().top;
            const elementRect = targetElementRef.current.getBoundingClientRect().top;
            const elementPosition = elementRect - bodyRect;
            const offsetPosition = elementPosition - offset;

            window.scrollTo({
                top:offsetPosition,
                behavior: 'smooth'
            });
          };

        
        // window.scrollBy({
        // top: 950, // Change this value to scroll by a different amount
        // left: 0,
        // behavior: 'smooth' // Optional: Adds smooth scrolling
        // });
    };

    return(
    <div className="self-introduction-container">
        <div className='introduction-container'>
            <h3>
                #Re-Use for Living”  Atelier 4 TZ | 6. Semester | FS 24
            </h3>
            <br/>
            <p>website for material query</p>
            <Button className ='button' onClick = {scrollToElement}>Find out More</Button>

        </div>

    </div>
    )
};

export default Introduction;