const parseKeywordListString = (keywordsString) => {
    // Suppose there are several keywords and we try separating them by any possible separator before adding
    // It also should be possible to get quoted keyword phrases
    const quotedKeywords = (keywordsString.match(/"([^"]+)"/g) || [])
        .map(k => k.replace(/"/g, "")); // remove quotes

    const remaining = keywordsString.replace(/"([^"]+)"/g, ""); // strip quoted parts
    const unquotedKeywords = remaining.split(/[\s,;|]+/).filter(Boolean);

    const resultList = [...quotedKeywords, ...unquotedKeywords];
    return resultList;
}


export { 
    parseKeywordListString
}