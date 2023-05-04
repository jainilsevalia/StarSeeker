let d = new Date();
let currentMonth = d.getMonth();

document.querySelector("#month").value = String(currentMonth);

const handleChange = () => {
  const month = document.querySelector("#month").value;
  const year = document.querySelector("#year").value;
  changeCalendar(month, year);
};

const removeElementsByClass = (className) => {
  let elements = document.getElementsByClassName(className);
  while (elements.length > 0) {
    elements[0].parentNode.removeChild(elements[0]);
  }
};

// const setBookedDate = (td,day) => {
//   //
// }

const setNonAvailibility = (td, day) => {
  if (td.classList.contains("not-available-date")) {
    td.classList.remove("not-available-date");
  } else {
    td.setAttribute("class", "not-available-date");
  }
};

const writeDateInCell = (td, count) => {
  const number = document.createTextNode(String(count));
  td.style.cursor = "pointer";
  td.addEventListener("click", () => setNonAvailibility(td, count));
  // setBookedDate(td,count);
  td.appendChild(number);
};

const changeCalendar = (month, year) => {
  let d = new Date(year, month, 1);
  let n = d.getDay();
  let currentDate = new Date().getDate();

  const newMonth = parseInt(month) + 1;
  const totalDays = new Date(year, newMonth, 0).getDate();

  const totalRows = Math.ceil((totalDays + n) / 7);

  const calender = document.querySelector("#calender");
  const monthSelector = document.querySelector("#month").value;

  removeElementsByClass("calRow");

  let count = 1;
  let blank = 1;
  for (let i = 1; i <= totalRows; i++) {
    const tr = document.createElement("tr");
    tr.classList.add("calRow");
    for (let j = 1; j <= 7; j++) {
      const td = document.createElement("td");
      if (count === currentDate && monthSelector === String(currentMonth)) {
        td.setAttribute("class", "current-date");
      }
      if (i !== 1) {
        if (count <= totalDays) {
          writeDateInCell(td, count);
          count += 1;
        }
      } else {
        if (blank > n) {
          writeDateInCell(td, count);
          count += 1;
        } else {
          blank += 1;
        }
      }
      tr.appendChild(td);
    }
    calender.appendChild(tr);
  }
};

const month = document.querySelector("#month").value;
const year = document.querySelector("#year").value;
changeCalendar(month, year);
