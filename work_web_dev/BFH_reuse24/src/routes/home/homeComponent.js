import Introduction from '../../components/self-introduce/self-introduceComponenet.js'
import HomeCards from '../../components/home-card/homeCardsComponent.js'

import './homeComponentStyle.scss'

import segmentation2 from '../../assets/segmentation2.png'
import rhino1 from '../../assets/rhino1.gif'
import rhino2 from '../../assets/rhino2.gif'
import { useRef } from 'react'


const Home = () =>{
    const targetElementRef = useRef(null)
    
    return(
        <div>
            <div className='top-container'></div>
            <Introduction targetElementRef = {targetElementRef}/>
            {/* <Directory categories= {categories}/>s */}
            <div className='content-wrapper'>
                <div className='home-card-introduction-container'>
                    <div className='home-card-introduction-title' ref={targetElementRef}>
                        <div>
                            <h2>Aufgabenstellung Atelier </h2>
                            <p style={{fontSize : "15px", color: "rgb(50,50,50)"}}>About the Studio</p>
                        </div>
                    </div>
                    <div className='home-card-introduction-text'>
                        <p> 
                        Im Atelier «Re-Use for Living» geht es um die Suche nach Möglichkeiten, wie aus dem Bauteilkatalog des Rückbauprojekts Roche Süd, 
                        neue zweigeschossige Wohnbauten entworfen und gebaut werden können. 
                        Die Entwurfsstrategie im Kontext der Wiederverwendung von Bauteilen weicht vom herkömmlichen Ablauf des Planungsprozesses mit neu produzierten Materialien und Bauteilen ab. 
                        Das Bauen im Rahmen des technischen Kreislaufs (Re-Use) erfordert die Formulierung elementarer Regeln/Parameter/Prinzipen zur Fügung der einzelnen Bauteile zu einem Ganzen. 
                        So kann der notwendige Spielraum geschaffen werden, um nicht in Bezug auf Formfaktor und Materialität a priori definierte Elemente elegant in das Projekt zu integrieren. 
                        Dies bedeutet gleichzeitig, dass der architektonische Ausdruck (die Gestalt) sich bis zum Abschluss des Entwurfs wandelt.

                        </p>
                    </div>
                    <hr/>
                    
                </div>
                <div>
                    <HomeCards />
                </div>

                {/* <div className='segmentaion-section-container'>
                    <div className='segmentaion-section-left'>

                        <img src= {segmentation2}></img>
                        
                    </div>
                    <div className='segmentaion-section-right'>
                        <h2>Ai-aided 2D to 3D conversion</h2>
                        <p>
                            Simplify the integration of reusable materials into the design phase with use of Ai tools for 3D model generation
                            using text and images propmts , common data format from exisiting circular building materials selling website

                        </p>
                    
                    </div>
                </div> */}

                
                {/* <div className='rhino-section-container'>
                    <div className='rhino-section-left'>
                        <h2>Intuitive search engine and friendly computational method for 3D remap </h2>
                        <img src= {rhino2}></img>
                        <p>
                                A connection between 3D software and our cloud-based database. 
                                This link ensures Grasshopper accesses the most up-to-date list of available circular materials. 
                                Based on these different searching criteria, our system searches the database for the most fitting ciruclar matertials 
                                to replace existing components within the model. 

                        </p>
                    </div>
                    <div className='rhino-section-right'>
                        <img src= {rhino1}></img>


                    </div>
                </div> */}
                
                <div className='logo-section-container'>
                    {/* <hr/> */}
                    {/* <div className='logo-introduction-title'>
                        <h2 >ETH Chairs Collaboration</h2>
                    </div> */}
                    {/* <div className='logo-container'>
                        <img src='https://masterschool.climate-kic.org/wp-content/uploads/sites/8/2019/08/ETH-Zurich.jpg'
                        alt='ETH'></img>
                        <img src='https://media.licdn.com/dms/image/C560BAQEMsz8IKOuxCQ/company-logo_200_200/0/1607623018497?e=2147483647&v=beta&t=Y2jT0rLXT72m0Qjtkb-f5OmS0w28Xp2_R4kYDYta4W0'
                        alt='DBT'></img>
                        <img src='https://avatars.githubusercontent.com/u/32545728?s=280&v=4'
                        alt='GKR'></img>
                        <img src='https://images.squarespace-cdn.com/content/v1/636958d5f3f2ff2fd642811f/93dcfeeb-1fce-4805-b263-a9316c9c7ca1/logo_cea_square_transparant.png'
                        alt='CEA'></img>
                    </div> */}
                </div>
            </div>
            <div className='bottom-container'></div>
        </div>
    )}

export default Home