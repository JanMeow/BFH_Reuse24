import './search-selection.scss'
import {useContext, useState} from 'react';
import { SearchContext } from '../../context/searchContext';
import {ProductsContext} from '../../context/productsContext'



const SearchButtonAndField = ({id, name, displayName, onChange, type, state, ...props}) =>{
    const value = state[name] || '';

    // For max and min search, their name includes '/'

    switch(name){
        case 'anzahl':
        case 'tiefe':
        case 'breite':
        case 'hoehe':
            const value_max = state[name+ '/max'] || 0;
            const value_min = state[name+ '/min'] || 0;
            return(
                <div className='search-type-container'>
                    <div className='search-type-container-left'>
                        <input type = 'checkbox' id ={id} name = {name} value = {value} checked={value_max || value_min }/>
                        <label htmlFor={`${id}`} >{displayName}</label>
                    </div>
                    <div className='search-type-container-right'>
                        <input htmlFor ='Max' name = {name + '/max'} value = {value_max } type={type} min="0" max="500"  id="UpperRange" onChange={onChange}/>
                            <label htmlFor="Max">Max: {value_max}</label>
                        <input htmlFor ='Min' name = {name + '/min'} value = {value_min} type={type} min="0" max="500"  id="LowerRange" onChange={onChange}/>
                            <label htmlFor="Min">Min: {value_min}</label>
                    </div> 
                </div>
            )
        default:
            return(
                <div className='search-type-container'>
                    <div className='search-type-container-left'>
                        <input type = 'checkbox' id ={id} name = {name} value = {value} checked={value}/>
                        <label htmlFor={`${id}`} >{displayName}</label>
                    </div>
                    <div className='search-type-container-right'>
                        <input type={type} id = {id} name = {name} placeholder='search' onChange={onChange} value={value}></input>
                    </div> 
                </div>
            );
    };

};



const SearchButton = ({id, name, displayName, state, onChange}) =>{

    switch(name){
        // Numeric Data
        case 'anzahl':
            return(
                <SearchButtonAndField id ={id} name={name} displayName={displayName} onChange={onChange}
                type ='range' state = {state}/>
            )
        case 'tiefe':
        case 'breite':
        case 'hoehe':
            // Currently we still have false as null attribute
            return(
                <SearchButtonAndField id ={id} name={name} displayName={displayName} onChange={onChange}
                type ='range' state = {state}/>
            )
        default:
            <SearchButtonAndField id ={id} name={name} displayName={displayName} onChange={onChange}
                type ='text' state = {state}/>
    }
};


const ResetButton = ({id, onClick})=>(
    <div className='search-type-container'>
        <button type = 'button' id ={id} onClick={onClick}>Reset</button>
    </div>
)

const SearchSelection = ({searchTypesShow}) =>{
    const {searchField, setSearchField} = useContext(SearchContext);


    const setSearchFieldChange = (event) =>{
        setSearchField({...searchField, [event.target.name]: event.target.value});
    };



    const resetSearchFeaturesHandler = ()=>{
        setSearchField({})
    }

    return(
        <div className="search-selections-containers">            
            {searchTypesShow&&
            <div>
                <form className='search-selections' id='search-selections'>
                    <div className='search-selections-middle'>
                        <SearchButton id ='searchByDimension' name = 'tiefe' displayName = 'Search by  (Tiefe)' 
                         onChange={setSearchFieldChange} state ={searchField}/>
                         <SearchButton id ='searchByDimension' name = 'breite' displayName = 'Search by Width (Breite)' 
                         onChange={setSearchFieldChange} state ={searchField}/>
                         <SearchButton id ='searchByDimension' name = 'hoehe' displayName = 'Search by Height (Hoehe)' 
                         onChange={setSearchFieldChange} state ={searchField}/>
                        <SearchButton id = 'searchByQuantity' name = 'anzahl' displayName = 'Search by Quantity (Anzahl)' 
                        onChange={setSearchFieldChange} state ={searchField}/>
                        <ResetButton id ='reset' onClick={resetSearchFeaturesHandler} />
                    </div>
                </form>
            </div>
            }
        </div>
    );
};

export default SearchSelection;