import HomeCard from './homeCardComponent';
import { useState } from 'react';
import './homeCardStyle.css'

// const cardInfo = 
// [

//   {
//     title: 'Aeussere_Wandbekleidung_Ueber_Terrain',
//     imageURl: "https://naturstein-teak.de/cdn/shop/files/TravertinScabasAntikWandverblenderSteinwandNaturstein-5_800x.jpg?v=1705134206"
//   },
//   {
//     title: 'Bauwerk_In_der_Umgebung',
//     imageURl: "https://cdn.shopify.com/s/files/1/0635/0553/1121/products/Dune_01.jpg?v=1655811745"
//   },
//   {
//     title: 'Befoerderungsanlage',
//     imageURl: "https://www.edl.poerner.de/fileadmin/_processed_/f/8/csm_3D_printed_model_HyKero_16x9_eaaac6af06.jpg"
//   },
//   {
//     title: 'Bodenbelag',
//     imageURl: "https://www.fussboden-wolf.de/themes/printeri/images/sl1.jpg"
//   },
//   {
//     title: 'Deckenbekleidung',
//     imageURl: "https://www.schmitz-peter.de/ab/600_399/2N4A9337.JPG"
//   },
//   {
//     title: 'Deckenkonstruktion',
//     imageURl: "https://www.ingenieurbau-online.de/fileadmin/_processed_/3/f/csm_tu-berlin_Kindergarten-innenansicht_Sissach_d5aa69db8f.jpg"
//   },
//   {
//     title: 'Schutzeinrichtung',
//     imageURl: "https://www.pilz.com/imagecache/mam/pilz/content/editors_mm/fittosize__752_0_a24c6b60bac4d6bfa5a5bea0c197f631_f_hannover_messe_psensgate_cold1_2012_04_v2-mobile-1698418345.jpg"
//   },
//   {
//     title: 'Aussenwand',
//     imageURl: "https://www.obi.de/api/disc/cms/public/dam/DE-AT-Assets/Wand/wand-mauern-porenbeton/mauer-verspachteln.jpg"
//   },
//   {
//     title: 'Bodenplatte',
//     imageURl: Bodenplatte
//   },
//   {
//     title: 'Hartflaeche',
//     imageURl: "https://images.pexels.com/photos/7931/pexels-photo-7931.jpg?cs=srgb&dl=pexels-pixabay-7931.jpg&fm=jpg"
//   },
//   {
//     title: 'Kleininventar',
//     imageURl: "https://www.shipbob.com/wp-content/uploads/2021/07/inventory-vs-stock-.jpg"
//   },
//   {
//     title: 'Lufttechnische_Anlage',
//     imageURl: "https://static.wixstatic.com/media/62adbcec8fc243d0b710789bb01af4a1.jpg/v1/fill/w_640,h_660,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/62adbcec8fc243d0b710789bb01af4a1.jpgg"
//   },
//   {
//     title: 'Mobiliar',
//     imageURl: "https://cooee.eu/wp-content/uploads/sites/2/2022/09/Mo%CC%88bler.jpg"
//   },
//   {
//     title: 'Stuetzenkonstruktion',
//     imageURl: "https://www.dbz.de/imgs/102489628_67fe1735e1.jpg"
//   },
//   {
//     title: 'Trennwand',
//     imageURl: "https://www.selbst.de/assets/field/image/trennwand-bauen.jpg"
//   },
//   {
//     title: 'Waermetechnische_Anlage',
//     imageURl: "https://www.advancedcooling.co.uk/wp-content/uploads/2023/01/Temperature-Control-3.jpg"
//   },
//   {
//     title: 'Nutzungsspezifische_Anlage',
//     imageURl: "https://www.pbb-engineering.de/files/cto_layout/img/leistungen/Nutzungsspezifische_Anlagen.jpg"
//   },
//   {
//     title: 'Wandbekleidung',
//     imageURl: "https://shop.beendorfer-massivholz.de/media/catalog/10/5c5b6f4149505398b938e4644dd915b2.jpg"
//   },
//   {
//     title: 'Wandkonstruktion',
//     imageURl: "https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.schwaebisch-hall.de%2Fratgeber%2Fsanieren-und-modernisieren%2Finnenausbau%2Ftrockenbau.html&psig=AOvVaw2CwnSbu3LpECKGndGFalj4&ust=1709382493955000&source=images&cd=vfe&opi=89978449&ved=0CBMQjRxqFwoTCJicvpSI04QDFQAAAAAdAAAAABAR"
//   },
//   {
//     title: 'Wassertechnische_Anlage',
//     imageURl: Wassertechnische_Anlage
//   },


// ]

const cardInfo = [
    {   
        id:'m0',
        imageUrl:"https://naturstein-teak.de/cdn/shop/files/TravertinScabasAntikWandverblenderSteinwandNaturstein-5_800x.jpg?v=1705134206",
        name: 'Aeussere_Wandbekleidung_Ueber_Terrain'
    },
    {   
        id:'m1',
        imageUrl: "https://cdn.shopify.com/s/files/1/0635/0553/1121/products/Dune_01.jpg?v=1655811745",
        name: 'Bauwerk In der Umgebung'
    },
    {   
        id:'m2',
        imageUrl:"https://www.edl.poerner.de/fileadmin/_processed_/f/8/csm_3D_printed_model_HyKero_16x9_eaaac6af06.jpg",
        name: 'Befoerderungsanlage'
    },
    {   
        id:'m3',
        imageUrl:"https://www.fussboden-wolf.de/themes/printeri/images/sl1.jpg",
        name: 'Bodenbelag'
    },
    {   
        id:'m4',
        imageUrl:"https://www.schmitz-peter.de/ab/600_399/2N4A9337.JPG",
        name: 'Deckenbekleidung'
    },
    {   
        id:'m5',
        imageUrl:"https://www.ingenieurbau-online.de/fileadmin/_processed_/3/f/csm_tu-berlin_Kindergarten-innenansicht_Sissach_d5aa69db8f.jpg",
        name: 'Deckenkonstruktion'
    },
    {   
        id:'m6',
        imageUrl:"https://www.pilz.com/imagecache/mam/pilz/content/editors_mm/fittosize__752_0_a24c6b60bac4d6bfa5a5bea0c197f631_f_hannover_messe_psensgate_cold1_2012_04_v2-mobile-1698418345.jpg",
        name: 'Schutzeinrichtung'
    },
    {   
        id:'m7',
        imageUrl:"https://www.obi.de/api/disc/cms/public/dam/DE-AT-Assets/Wand/wand-mauern-porenbeton/mauer-verspachteln.jpg",
        name: 'Aussenwand'
    },
    {   
        id:'m8',
        imageUrl:"https://images.pexels.com/photos/7931/pexels-photo-7931.jpg?cs=srgb&dl=pexels-pixabay-7931.jpg&fm=jpg",
        name: 'Hartflaeche'
    },
    {   
        id:'m9',
        imageUrl:"https://www.shipbob.com/wp-content/uploads/2021/07/inventory-vs-stock-.jpg",
        name: 'Kleininventar'
    },
    {   
        id:'m10',
        imageUrl:"https://static.wixstatic.com/media/62adbcec8fc243d0b710789bb01af4a1.jpg/v1/fill/w_640,h_660,al_c,q_85,usm_0.66_1.00_0.01,enc_auto/62adbcec8fc243d0b710789bb01af4a1.jpgg",
        name: 'Lufttechnische Anlage'
    },
    {   
        id:'m11',
        imageUrl:"https://cooee.eu/wp-content/uploads/sites/2/2022/09/Mo%CC%88bler.jpg",
        name: 'Mobiliar'
    },
    {   
        id:'m12',
        imageUrl:"https://www.dbz.de/imgs/102489628_67fe1735e1.jpg",
        name: 'Stuetzenkonstruktion'
    },
    {   
        id:'m13',
        imageUrl:"https://www.selbst.de/assets/field/image/trennwand-bauen.jpg",
        name: 'Trennwand'
    },
    {   
        id:'m14',
        imageUrl:"https://www.advancedcooling.co.uk/wp-content/uploads/2023/01/Temperature-Control-3.jpg",
        name: 'Waermetechnische Anlage'
    },
    {   
        id:'m15',
        imageUrl:"https://www.pbb-engineering.de/files/cto_layout/img/leistungen/Nutzungsspezifische_Anlagen.jpg",
        name: 'Nutzungsspezifische Anlage'
    },
    {   
        id:'m16',
        imageUrl:"https://shop.beendorfer-massivholz.de/media/catalog/10/5c5b6f4149505398b938e4644dd915b2.jpg",
        name: 'Wandbekleidung'
    },
    {   
        id:'m16',
        imageUrl:"https://shop.beendorfer-massivholz.de/media/catalog/10/5c5b6f4149505398b938e4644dd915b2.jpg",
        name: 'Wandbekleidung'
    },
    {   
        id:'m16',
        imageUrl:"https://shop.beendorfer-massivholz.de/media/catalog/10/5c5b6f4149505398b938e4644dd915b2.jpg",
        name: 'Wandbekleidung'
    },

]


const HomeCards = () =>{

    const [expandedIndex, setExpandedIndex] = useState({upperbound: 5, lowerbound:0});
    const [showArrow, setshowArrow] = useState({right: true, left:false});


   const scrollHandler = (direction)=>{
    switch(direction){
        case 'Right':
            if(expandedIndex.upperbound< cardInfo.length){
                setExpandedIndex({...expandedIndex,upperbound: expandedIndex.upperbound +1, lowerbound: expandedIndex.lowerbound +1 } )
                setshowArrow({...showArrow,right: !showArrow.right})
            }
            break;
        case 'Left':
            if(expandedIndex.lowerbound> 0){
                setExpandedIndex({...expandedIndex,upperbound: expandedIndex.upperbound -1, lowerbound: expandedIndex.lowerbound -1} )
                setshowArrow({...showArrow,left: !showArrow.left})
            }
            break;
    }
   };



    return(
        <div className='home-component-container'>
            <div className='cards-title'>
                    <h3> Bauteilkatalog des Rueckbauprojekts Roche Sued </h3>
                    <p >
                        Die Roche hat mit Hilfe von Gruner Ingenieure einen Bauteilkatalog erstellt, 
                        in dem ein Grossteil der Bauteile erfasst sind. Die erste Atelierdurchführung im Frühling 2023 zeigte jedoch, 
                        dass es durchaus auch verwendbare Bauteile in den Bauten gibt, die nicht im Katalog erfasst sind. 
                        Beispielsweise Wasserrohre, Kabel, Lueftungsrohre, Teppiche, Eckbleche, Daemmmaterialien, etc. 
                        Aus diesem Grund bedarf es den Beizug weiterer Quellen um die Aufgabe 100% Re-Use-for-living erfüllen zu können.
                    </p>
            </div>
            
            <div className='scroll-wrapper'>
                <div className='left-arrow-container' onClick={()=>scrollHandler('Left')} >&#60;</div> 
                <div className="cards-list">
                    {cardInfo.slice(expandedIndex.lowerbound,expandedIndex.upperbound).map((element)=>(
                        <HomeCard info ={element}/>
                    ))}
                </div>
                <div className='right-arrow-container' onClick={()=>scrollHandler('Right')}>&#62;</div>
            </div>
        </div>

    );
};

export default HomeCards;