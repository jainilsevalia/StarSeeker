const faqList = document.querySelector("#faq-list");

const removeBtn = document.querySelector("#remove-faq");
let count = 1 + parseInt(document.querySelector("#faqs-length").value);
const setAttributes = (el, attrs) => {
  for (var key in attrs) {
    el.setAttribute(key, attrs[key]);
  }
};

const setBtns = () => {
  const faqItem = document.querySelectorAll(".faq-item");
  const addBtn = document.querySelector("#add-faq");
  if (faqItem.length === 1) {
    removeBtn.style.display = "none";
  } else {
    removeBtn.style.display = "initial";
  }
  if (count > 5) {
    addBtn.style.display = "none";
  } else {
    addBtn.style.display = "initial";
  }
};
setBtns();

const addFaq = () => {
  const li = document.createElement("li");
  li.classList.add("faq-item");
  const question = document.createElement("input");
  setAttributes(question, {
    type: "text",
    id: "que" + count,
    name: "que" + count,
    placeholder: "Question",
    class: "form-control w-75",
  });
  const div = document.createElement("div");
  const answer = document.createElement("textarea");
  setAttributes(answer, {
    id: "ans" + count,
    name: "ans" + count,
    placeholder: "Answer",
    class: "w-75 mt-2",
  });

  div.appendChild(answer);

  li.appendChild(question);
  li.appendChild(div);

  faqList.appendChild(li);
  count++;
  setBtns();
};

const removeFaq = () => {
  const faqItem = document.querySelectorAll(".faq-item");
  let lastFaq = faqItem[faqItem.length - 1];
  lastFaq.parentNode.removeChild(lastFaq);
  count--;
  setBtns();
};
