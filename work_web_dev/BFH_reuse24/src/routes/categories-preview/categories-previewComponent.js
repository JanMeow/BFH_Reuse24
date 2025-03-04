import { useState, useContext, Fragment } from "react";
import { Link } from "react-router-dom";
import SearchTypeStream from "../../components/searchtype/search-type-Stream";


import './categories-previewStyle.scss'

const CategoriesPreview = ({materialInfo, searchField}) =>{

   
    return(
        <Fragment>
            {
                materialInfo.map(element=>
                    {
                        const{title, items} = element
                        return(
                            <Fragment key = {title}>
                                <Link to = {`${title}`} className="navgation-title">
                                    <h2>{title.replaceAll("_", " ")} </h2>
                                </Link>
                                <div className="products-container">
                                    <SearchTypeStream items={items} searchField= {searchField} title = {title} 
                                    maxIndex= {4}/>
                                </div>
                            </Fragment>
                        )
                })}   
        </Fragment>

    );
};



export default CategoriesPreview;