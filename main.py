from fastapi import FastAPI, HTTPException, Depends, status, Query
from contextlib import asynccontextmanager
from database import init_db, get_session
from models import StringRequestBody, StringProperty
from sqlmodel import Session, select
from typing import Optional


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

@app.post("/strings")
def analyze_string(data: StringRequestBody, db: Session = Depends(get_session)):
    hash_id = StringProperty.generate_hash(data.value)

    existing = db.get(StringProperty, hash_id)
    if existing:
        raise HTTPException(status_code=400, detail="String already exists in the DB, Try another String")
    
    properties: dict = {}
    # Length
    properties['length'] = len(data.value)
    
    # Check if Palindrome and for unique characters
    reversed_value = ""
    seen = []
    unique_characters = 0
    for i in range(len(data.value) - 1, -1, -1):
        value = data.value[i]
        reversed_value += value

        if value.lower() not in seen:
            unique_characters += 1
            seen.append(value.lower())

    properties["is_palindrome"] = True if reversed_value == data.value else False
    properties["unique_characters"] = unique_characters

    # Genrate Word Count
    words = data.value.split(" ")
    properties["word_count"] = len(words)

    # Generate SHA256 hash
    properties["sha256_hash"] = StringProperty.generate_hash(data.value)

    # Generate Character Frequency Map
    character_frequency_map = {}
    for char in data.value.lower():
        if char not in character_frequency_map.keys():
            character_frequency_map[char] = 1
        else:
            character_frequency_map[char] += 1
    properties["character_frequency_map"] = character_frequency_map

    # Generate Hash for id
    string_record = StringProperty.create(
        value = data.value,
        properties=properties
    )
    
    db.add(string_record)
    db.commit()
    db.refresh(string_record)
    return string_record


@app.get("/strings/filter-by-natural-language")
def filter_strings_natrual_language(query: str = None, 
                                    db: Session = Depends(get_session)):
    db_query = select(StringProperty)
    parsed_filters = {}

    if query == "all single word palindromic strings":
        db_query = db_query.where(StringProperty.properties["is_palindrome"].as_boolean() == True) \
                                  .where(StringProperty.properties["word_count"].as_integer() == 1)
        parsed_filters = {
            "word_count": 1,
            "is_palindrome": True
        }
        
    elif query == "strings longer than 10 characters":
        db_query = db_query.where(StringProperty.properties["length"].as_integer() > 10)

        parsed_filters = {
            "min_length": 11
        }

    elif query == "palindromic strings that contain the first vowel":
        db_query = db_query.where(StringProperty.properties["is_palindrome"].as_boolean() == True) \
                        .where(StringProperty.value.contains("a"))
        
        parsed_filters = {
            "is_palindrome": True,
            "contains_character": "a"
        }
    
    elif query == "strings containing the letter z":
        db_query = db_query.where(StringProperty.value.contains("z"))

        parsed_filters = {
            "contains_character": "z"
        }
        
    results = db.exec(db_query).all()

    # Construct Response
    return {
        "data": results,
        "count": len(results),
        "interpreted_query": {
            "original": query,
            "parsed_filters": parsed_filters
        }
    }


@app.get("/strings/{string_value}")
def get_string(string_value: str, db: Session = Depends(get_session)):
    result = db.exec(
        select(StringProperty).where(StringProperty.value == string_value)
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="String not found")

    return result


@app.get("/strings")
def get_strings(is_palindrome: Optional[bool] = Query(None),
                min_length: Optional[int] = Query(None, ge=0),
                max_length: Optional[int] = Query(None, ge=0),
                word_count: Optional[int] = Query(None, ge=1),
                contains_character: Optional[str] = Query(None, min_length=1, max_length=1),
                db: Session = Depends(get_session)):
    query = select(StringProperty)

    if is_palindrome is not None:
        query = query.where(StringProperty.properties["is_palindrome"].as_boolean() == is_palindrome)

    if min_length is not None:
        query = query.where(StringProperty.properties["length"].as_integer() >= min_length)

    if max_length is not None:
        query = query.where(StringProperty.properties["length"].as_integer() <= max_length)

    if word_count is not None:
        query = query.where(StringProperty.properties["word_count"].as_integer() == word_count)

    if contains_character:
        query = query.where(StringProperty.value.contains(contains_character))


    results = db.exec(query).all()

    # Construct Response
    return {
        "data": results,
        "count": len(results),
        "filters_applied": {
            "is_palindrome": is_palindrome,
            "min_length": min_length,
            "max_length": max_length,
            "word_count": word_count,
            "contains_character": contains_character,
        }
    }
    


@app.delete("/strings/{string_value}", status_code=status.HTTP_204_NO_CONTENT)
def delete_string(string_value: str, db: Session = Depends(get_session)):
    result = db.exec(
        select(StringProperty).where(StringProperty.value == string_value)
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="String not found")
    
    db.delete(result)
    db.commit()
    return None
