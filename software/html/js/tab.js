function setTab(index) {
            const list = document.querySelectorAll(".tabbar ul li");
            const slider = document.querySelector(".slider");
            list.forEach(l => l.classList.remove("active"))
            console.log(index)
            list[index].classList.add("active")
            slider.style.transform = `translateX(-${index * 100}%)`


        }