import React from "react";
import'./material-detailStyle.scss'
import { Link } from "react-router-dom";
import Button from "../button/buttonComponent";


const Inline = ({item})=>{
    const attributes = Object.keys(item);

    return attributes.map(attribute =>{
        const skip = ['uuid', 'image', 'url', 'id', 'model', 'co2' , 'kosten' , 'masse',
    'foto1', 'foto2', 'bauteil_gruner']
        if(skip.includes(attribute)){return}
        return(
            <div className = 'attribute'>
                <h4 className="attribute-title">
                    {`${attribute} :  `} 
                    <span className="attribute-content">{`${item[attribute]}`}</span>          
                </h4>
                
            </div>
        )
    })
}


const MaterialDetail = ({title, item})=>{

    return(
        <div className="material-detail-section-wrapper">
            <h3>
                <Link to= '/'>HOME</Link>
                &#62;
                <Link to={`/shop/${title}`}>{title.toUpperCase()}</Link>
                &#62;
                <Link to= {`/shop/${title}/${item.uuid}`}>{item.uuid.toUpperCase()}</Link>

            </h3>
            <div className="material-detail-section">
                <div className="material-image">
                        <img src = {item.foto1} />
                </div>
                <div className="material-info">
                    <div className="material-info-header">
                    <h2>{item.bauteil_gruner} </h2>
                    <p style={{fontSize: "16px", color: "rgb(70,70,70)"}}>{item.uuid}</p>
                    <hr></hr>
                    </div>
                    <div className="material-info-body">
                        <Inline item ={item}/>
                        <div className="material-info-body-button"> 
                            <Button buttonType='inverted'> Add to Cart</Button>
                        </div>
                    </div>
                    

                </div>

            </div>
        </div>

    )
}

export default MaterialDetail


