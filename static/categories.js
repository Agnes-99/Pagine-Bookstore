//Change the category name

function getSelectedCategory(){

    document.addEventListener("DOMContentLoaded", function () { 
    
    let categories = document.querySelectorAll(".categories");
    categories = Array.from(categories);

    categories.forEach(element => {
        element.addEventListener('click', function () {
            let userSelection = this.textContent.trim();
            localStorage.setItem("selectedCategory", userSelection);
            window.location.href ="C:\Users\agnes\OneDrive\Desktop\Pagine Book Store\flask project\Templates\category.html"
        //changeCategories(userSelection);
    });
});
});
}

function changeCategories() {
      
    document.addEventListener("DOMContentLoaded",function(){

        const selectedCategory = localStorage.getItem("selectedCategory");
        const headingElement = document.getElementById("category-heading");

        if (headingElement && selectedCategory) {
        headingElement.innerHTML = selectedCategory;
        localStorage.remove("selectedCategory");
        } 
    else if(!headingElement) {
        console.warn("Element with ID 'category-heading' not found.");
    }
    });
       
 }