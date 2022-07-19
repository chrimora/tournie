document.getElementById("pass").addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        document.getElementById("next_btn").click();
    }
})

function showTab(n) {
    var tabs = document.getElementsByClassName("tab");
    tabs[n].style.display = "block";

    if (n == (tabs.length - 1)) {
        document.getElementById("next_btn").innerHTML = "Submit";
    } else {
        document.getElementById("next_btn").innerHTML = "Next";
    }
}

function nextPrev(n) {
    var tabs = document.getElementsByClassName("tab");
    tabs[currentTab].style.display = "none";

    currentTab = currentTab + n;
    if (currentTab >= tabs.length) {
        document.getElementById("account_form").submit();
    } else {
        showTab(currentTab);
    }
}

var currentTab = 0;
showTab(currentTab);
