
const menuToggle = document.getElementById("menuToggle");
const menu = document.getElementById("menu");

menuToggle.addEventListener("click", function (event){
    menu.classList.toggle("hidden");
    event.stopPropagation();
});


document.addEventListener("click", function (event){
   if(!menu.contains(event.target) && !menuToggle.contains(event.target)){
       menu.classList.add("hidden");
   }
});

