function MakePost(event) {
    event.preventDefault(); 
    window.location.href = "/makepost";
}


function welcome() {

    document.getElementById("paragraph").innerHTML += "<br/>This text was added by JavaScript 😅";

    document.addEventListener("DOMContentLoaded", function() {
        const postButton = document.getElementById("post-button");
    
        postButton.addEventListener("click", MakePost);
    });
    
}
document.addEventListener("DOMContentLoaded", function() {
    const postButton = document.getElementById("post-button");
    
    postButton.addEventListener("click", MakePost);
    welcome();
});