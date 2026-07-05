// Sidebar Active Link

const links = document.querySelectorAll(".sidebar a");

links.forEach(link => {

    link.addEventListener("click", function(){

        links.forEach(item => item.classList.remove("active"));

        this.classList.add("active");

    });

});


// Welcome Message

console.log("AI Payment Dashboard Loaded Successfully");

const fileInput = document.getElementById("fileInput");

const fileInfo = document.getElementById("fileInfo");

if(fileInput){

fileInput.addEventListener("change",function(){

const file=this.files[0];

if(file){

fileInfo.innerHTML=`
<b>Selected File:</b> ${file.name}<br>
<b>Size:</b> ${(file.size/1024).toFixed(2)} KB
`;

}

});

}

const uploadForm=document.getElementById("uploadForm");

if(uploadForm){

uploadForm.addEventListener("submit",async function(e){

e.preventDefault();

const formData=new FormData();

formData.append("file",fileInput.files[0]);

const response=await fetch("/analyze",{

method:"POST",

body:formData

});

const data=await response.json();

if (data.success) {

    localStorage.setItem("analysis", data.result);

    window.location.href = "/analysis";

} else {

    alert(data.error);

}

});

}