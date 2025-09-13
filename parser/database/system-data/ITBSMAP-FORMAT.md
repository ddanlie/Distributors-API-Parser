### .itbsmap format is a custom format for easy auto/manual data mapping

For each of 3 file name types, .itbsmap is defining 3 different map specifications:

1. `categories.itbsmap` file is mapping distributors categories to generally defined categories
2. `properties.<general_category_id>.itbsmap` file maps distributor category properties to general category properties
3. `itemdata.itbsmap` file defines how each distributor item info is mapped to a general item data field


Specifications:

1. Categories mapping example:

    - File starts with optional meta declarations (or nothign and next line by format) - one declaration per line: #ALLOW_GENERAL_DUPLICATES #ALLOW_LOCAL_DUPLICATES etc
    - Empty line
    - Next line starts is general catgegories definition
    - Next line is empty line
    - After general categories definition - distributors categories section starts
    - Each distributor category group is started with a new line, then line with distributor name, then categories themselves.
    - The file is finished with 1 or more empty lines
    
        1.1. General categories definition (< and > are not included, | means "OR"):
        ```
        #ALLOW_LOCAL_DUPLICATES
        <empty line>
        <General category name>
        <General category name 2>
        <4 spaces | tab><General subcategory name>
        <4 spaces | tab><4 spaces | tab><Any distributor category/subcategory name><1 or more spaces><:><DB (not from local distributor) id of this category>
        <4 spaces | tab><Any distributor category/subcategory name><1 or more spaces><:><DB (not from local distributor) id of this category>
        <empty line>
        ```

        1.1.1 Explanation
        - First line says: we can add distributors categories to general categories more than once
        - 2nd line declares empty general category
        - 3rd line declares non empty general category
        - 4th line declares general subcategory
        - and 5th line says we will add contents of one of distributors categories to this subcategory
        - 6th line line says we will add contents of one of distributors categories to this general category - it will not intersect with the contents of its subcategory

        1.1.2 Comments
        - If you work manually - distributors categories just copied under any general category and general category is declared by yourself for the first db fill
        - Each time DB is refilled and remapped with general categories and its contents
        


        1.2 Distributors categories definition
        ```
        <empty line>
        <distributor name>
        <Distr. cat. name><1 or more spaces><:><DB (not from local distributor) id of this category>
        <4 spaces | tab><Distr. subcat. name><1 or more spaces><:><DB (not from local distributor) id of this category>
        <empty line>
        <distributor name 2>
        <Distr. cat. name><1 or more spaces><:><DB (not from local distributor) id of this category>
        <empty line>
        ```

        1.2.1 Explanation
        - This section is not really generated manually and you have to only copy fields from here
        - The indentation is not checked during parsing in this section

        1.2.2 Comments
        - On first db fill and map file generation - only this section will be shown
