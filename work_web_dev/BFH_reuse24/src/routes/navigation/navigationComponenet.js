import { Fragment, useContext, useState } from "react";
import { Outlet, Link } from "react-router-dom";
import './navigationStyle.scss';
import CartIcon from "../../components/cart-icon/cart-iconComponenet";
import CartDropdown from "../../components/cart-dropdown/cart-dropdownComponent";
import SearchSelection from "../../components/searchtype/search-selectionComponenet";
import SearchButton2 from "../../components/button2/Button2";

import { UserContext } from "../../context/userContext";
import { CartContext } from "../../context/cartContext";
import { useLocation } from "react-router-dom";


import { signOutUser } from "../../utils/firebase/firebaseUtils";



const Navigation = ()=>{
    const {currentUser} = useContext(UserContext);
    const {isCartOpen} = useContext(CartContext);

    const [searchTypesShow, setsearchTypesShow] = useState(false);


    const signOutHandler = async ()=>{
        await signOutUser();
    }

    const showSearchTypeHandler = () =>{
        setsearchTypesShow(!searchTypesShow)
        
    }

    const location = useLocation();
    const location_bool = location.pathname == "/"
    
    console.log(location.pathname) 
    return(
      <Fragment>
        <div className="header" style={{position: location_bool?"sticky":"static"}}>
            <div className="front-line"></div>
            <h2 className="title"> 
                <span style={{fontStyle :"italic", fontWeight:'300'}}>#_ _ </span> 
                Re-Use for Living”  Atelier 4 TZ | 6. Semester | FS 24
                <span style={{fontStyle :"italic", fontWeight:'300'}}>_ _# </span>
            </h2>
            <div className="navigation">
                <div className="logo-container">
                    <Link to ='/' >
                        @HOME
                    </Link>
                    <Link to ='https://airtable.com/app5ipW52XLtxkeb2/pagRB9O8tnOeKydJd/form'>
                        @Angaben hinzufügen
                    </Link>
                </div>
                
                <div className="nav-links-container">
                    <div className="search-elements-container">
                        <SearchButton2 onClick={showSearchTypeHandler} 
                        content = {searchTypesShow? "Close Bar": "=> Start Search"}/>             
                    </div>
                    <Link className="nav-link" to='/shop'>
                        @Browse Bauteile
                    </Link>
                    {currentUser?(<span className="nav-link" onClick={signOutHandler}> SIGN OUT</span>)
                    :(
                    <Link className="nav-link" to='/auth'>
                    @SIGNIN
                    </Link>)
                    }
                    <CartIcon/>
                </div>
                {isCartOpen &&<CartDropdown/>}
            </div>
            <div className="bottom-search-type-container">
                <SearchSelection searchTypesShow={searchTypesShow}/>
            </div>
        </div>
        <Outlet/>
      </Fragment>
    );
  };


  export default Navigation