const linkList = document.querySelector("#embed-video-list");

const removeLinkItemBtn = document.querySelector("#remove-video-link");
let linkItemCount = 1 + parseInt(document.querySelector("#links-length").value);

const setLinkBtns = () => {
  const linkItem = document.querySelectorAll(".embed-video-item");
  const addBtn = document.querySelector("#add-video-link");
  if (linkItem.length === 1) {
    removeLinkItemBtn.style.display = "none";
  } else {
    removeLinkItemBtn.style.display = "initial";
  }
  if (linkItemCount > 5) {
    addBtn.style.display = "none";
  } else {
    addBtn.style.display = "initial";
  }
};
setLinkBtns();

const addVideoLink = () => {
  linkList.innerHTML += `
    <li class="embed-video-item d-initial d-lg-flex align-items-center ml-3 ml-lg-0 mt-0 mt-lg-2">
        <span class="d-none d-lg-block">${linkItemCount}. https://www.youtube.com/embed/</span>
        <input
            type="text"
            id="embed-video-${linkItemCount}"
            name="embed-video-${linkItemCount}"
            placeholder="Enter youtube video id"
            class="form-control w-auto ml-1"
        />
    </li>
    `;
  linkItemCount++;
  setLinkBtns();
};

const removeVideoLink = () => {
  const linkItem = document.querySelectorAll(".embed-video-item");
  let lastLintItem = linkItem[linkItem.length - 1];
  lastLintItem.parentNode.removeChild(lastLintItem);
  linkItemCount--;
  setLinkBtns();
};
