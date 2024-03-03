import Button from "../button/buttonComponent";

import { useContext} from "react";
import { CartContext } from "../../context/cartContext";

import './material-cardStyle.scss';

const MaterialCard = ({material, title}) =>{
    const {uuid, bauteil_gruner, anzahl, foto1} = material;
    const {addItemToCart} = useContext(CartContext);


    const addProductToCart = ()=> addItemToCart(material);

    return(
        <div className="product-card-container">
            <a href={`/shop/${title}/${uuid}`}>
                <img src = {foto1} alt = {`${foto1}`}/>
            </a>
            <div className="footer">
                <span className= {bauteil_gruner}>Name: {bauteil_gruner}</span>
                <br></br>
                <span className= {anzahl}>In stock: {anzahl}</span>
            </div>
            <Button buttonType = 'inverted' onClick ={addProductToCart}> Add to cart</Button>
        </div>
    )
};

export default MaterialCard;