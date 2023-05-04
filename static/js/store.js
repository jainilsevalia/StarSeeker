function searchtext(){
    document.getElementById("searchform").submit()
}

function editbtnclick(){
    var btn = document.getElementById('editprofilebtn') 
    document.getElementById('saveprofilediv').classList.toggle('d-none')
    document.getElementById('staticName').toggleAttribute('disabled')
    if (btn.innerHTML == 'Edit'){
        btn.innerHTML = 'Cancel'
    }else{
        btn.innerHTML = 'Edit'
    }
}
