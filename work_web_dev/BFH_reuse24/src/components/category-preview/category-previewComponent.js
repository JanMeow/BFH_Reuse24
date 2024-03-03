import './category-previewStyle.scss';
import MaterialCard from '../home-card2/material-cardComponent';
import SearchTypeStream from '../searchtype/search-type-Stream';
import {Fragment} from 'react';




const CategoryPreview = ({materialInfo, searchField, title}) =>{

    const match = title

    return(
        <Fragment>
            {
                materialInfo.map(element=>
                    {
                        const{title, items} = element
                        if(title === match){
                            return(
                                <Fragment key = {title}>
                                    <h2 onClick = {()=>{console.log(match)}}>{title.replaceAll("_", " ")} </h2>
                                    <div className="products-container">
                                        <SearchTypeStream items={items} searchField= {searchField} title = {title} maxIndex= {items.length}/>
                                    </div>
                                </Fragment>
                            )
                        }
                })}   
        </Fragment>

    );
};

export default CategoryPreview;