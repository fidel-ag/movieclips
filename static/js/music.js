const evt1 = document.getElementById("addMoreBtn");
let mp3Counter = 2;// Initialize counter for MP3 uploads

evt1?.addEventListener("click", function (e) {
  e.preventDefault();
  const sectionContainer = document.getElementById("repeatable-block");
  const newSection = document.createElement("div");
  newSection.classList.add("section");

  // Create a new section for the MP3 upload
  const newSection1 = document.createElement("div");
  newSection1.classList.add("browse-field");
  
  // Use the counter to create unique IDs for the slider components
  const sliderId = `slider-${mp3Counter}`;
  const sliderFilledId = `slider-filled-${mp3Counter}`;
  const sliderThumbId = `sliderThumb-${mp3Counter}`;
  const valueLabelId = `valueLabel-${mp3Counter}`;
  const valuescrollId=`valuescrollId-${mp3Counter}`

  newSection1.innerHTML = `
    <div class="col-md-12" style="justify-content: space-between; display: flex; margin-top: 40px;">
      <label for="formFileLg" class="label-txt" style="padding-top: 5px;">Upload MP3 ${mp3Counter}:</label>
      <a href="#!" class="delete-music" style="padding: 10px 10px; border: 1px solid #3663ff; text-align: right;" id="blue-delete">Delete</a>
    </div>
    <br>
    <div class="custum-browse custum-browse-v2 d-flex align-items-center">
      <div class="brws">
        <input class="br-input" name="mp3[]" id="mp3[]" type="file" />
        <a href="#!" class="btn get-start browse-btn">
          <img src="/static/images/upload-icn-black.svg" alt="" /> Choose file
        </a>
      </div>
      <p></p>
    </div>`;

  // Create a new section for time input
  const newSection2 = document.createElement("div");
  newSection2.classList.add("browse-field");
  newSection2.innerHTML = `
    
    <div class="browse-field">
      <div>
        <div class="fontSize-Container">
          <label for="${sliderId}" class="label-txt" style="font-weight: bold;"
                        >MP3 ${mp3Counter}: Volume:</label
                      >
          <div class="slider-value" min id="${valueLabelId}">20%</div>
          <input class="slider-value-input" id="${valuescrollId}" name="volume[]" id="volume[]" value="20" hidden />
        </div>
        <div class="slider-container">
          <div class="slider-track">
            <div class="slider-filled" id="${sliderFilledId}"></div>
          </div>
          <div class="slider-thumb" id="${sliderThumbId}"></div>
        </div>
      </div>
    </div><br><label for="exampleInput" class="label-txt"  style="margin-bottom: 2px;">What Second Should This MP3 Play? <small>in minutes</small></label><!-- Volume Slider -->
    `;

  // Create a new section for start and end time input
  const newSection3 = document.createElement("div");
  newSection3.classList.add("time-fld");
  newSection3.innerHTML = `
    <div class="browse-field">
      <label for="starts[]" class="label-txt">Start:</label>
      <input type="text" placeholder="00:00"  name="starts[]" class="form-control" id="starts[]" aria-describedby="emailHelp" />
    </div>
    <div class="browse-field">
      <label for="ends" class="label-txt">End:</label>
      <input type="text" placeholder="00:00"  name="ends[]" class="form-control" id="ends[]" aria-describedby="emailHelp" />
    </div>`;

  // Append the heading and inputs to the new section
  newSection.appendChild(newSection1);
  newSection.appendChild(newSection2);
  newSection.appendChild(newSection3);
  sectionContainer.appendChild(newSection);

  // Add event listener to the delete button
  const deleteButton = newSection1.querySelector(".delete-music");
  deleteButton.addEventListener("click", function () {
    sectionContainer.removeChild(newSection); // Remove the specific section
    mp3Counter--; // Decrease the counter
    updateMP3Numbers(); // Update remaining sections' numbers
  });
  const fileInputs = document.querySelectorAll('.br-input');
  const noFileTexts = document.querySelectorAll('.btn.get-start.browse-btn');
  console.log(fileInputs,noFileTexts);
  fileInputs.forEach((input, index) => {
    input.addEventListener('change', (event) => {
      const fileName = event.target.files.length > 0 ? event.target.files[0].name.slice(0,12) : 'Choose file';
      noFileTexts[index].lastChild.textContent = fileName; // Update the text to show the selected file name
    });
  });
  
  // Initialize slider for the new MP3
  initSlider(sliderId, sliderFilledId, sliderThumbId, valueLabelId,valuescrollId);
  
  mp3Counter++;
});

// Function to initialize the slider
function initSlider(sliderId, filledId, thumbId, valueLabelId,valuescrollId) {
  const sliderThumb = document.getElementById(thumbId);
  const sliderFilled = document.getElementById(filledId);
  const valueLabel = document.getElementById(valueLabelId);
  const valuescrolllabel=document.getElementById(valuescrollId);
  const sliderContainer = sliderThumb.parentElement; // Get the slider container
  const trackWidth = sliderContainer.offsetWidth;

  let isDragging = false;

  sliderThumb.style.left = "20%";
  sliderFilled.style.width = "20%";
  // Define min and max values for the slider
  const minValue = 0;
  const maxValue = 100;

  function updateSliderPosition(event) {
    if (isDragging) {
      const rect = sliderContainer.getBoundingClientRect();
      const offsetX = event.clientX - rect.left; // Get the mouse position relative to the slider
      const percentage = Math.max(0, Math.min(offsetX / trackWidth, 1)); // Calculate the percentage
      const value = Math.round(percentage * (maxValue - minValue) + minValue); // Convert to 0-100 scale

      // Update the thumb position and the label value
      sliderThumb.style.left = `${percentage * 100}%`;
      sliderFilled.style.width = `${percentage * 100}%`;
      valueLabel.innerHTML = `${value}%`;
      valuescrolllabel.value=`${value}` // Append percentage symbol
    }
  }

  // Mouse down event to start dragging
  sliderThumb.addEventListener("mousedown", () => {
    isDragging = true;
  });

  // Mouse up event to stop dragging
  document.addEventListener("mouseup", () => {
    isDragging = false;
  });

  // Mouse move event to update the slider
  document.addEventListener("mousemove", updateSliderPosition);
}

// Function to update MP3 upload numbers
function updateMP3Numbers() {
  const sections = document.querySelectorAll("#repeatable-block .section");
  sections.forEach((section, index) => {
    const label = section.querySelector(".browse-field label");
    if (label) {
      label.textContent = `Upload MP3 ${index + 1}:`; // Update label text
    }
  });
}


const evt2 = document.getElementById("createLeadBtn");
let slideCounter = 4; // Start at 4 if you already have 3 slides

evt2?.addEventListener("click", function (e) {
  e.preventDefault();
  const sectionContainer = document.getElementById("leadsTable");
  const tbody = sectionContainer.querySelector("tbody");

  // Update existing slide numbers
  const slides = tbody.querySelectorAll("tr");
  slides.forEach((slide, index) => {
    const slideCell = slide.querySelector("td:first-child");
    slideCell.textContent = `Slide ${index + 2}`;
  });

  // Create a new section div for the new slide
  const newSection = document.createElement("tr");
  newSection.innerHTML = `
    <td>Slide 1</td> <!-- New slide will always be the first -->
    <td>
      <textarea style="font-size: 19px;" type="text" placeholder="Type Your Sentence Here" class="form-control tab-textarea" aria-describedby="textarea"  ></textarea>
    </td>

    <td style="background: none;">
      <div class="custum-browse custum-browse-v2 d-flex align-items-center">
        <div class="brws">
          <input class="br-input" type="file" >
          <a href="#!" class="btn get-start browse-btn">
            <img src="/static/images/upload-icn-black.svg" alt=""> Choose file
          </a>
        </div>
        <p></p>
      </div>
    </td>
    
    <td>
      <a href="#!" class="delete-row-btn">
        <img src="/static/images/delete-icn.svg" alt="delete">
      </a>
    </td>
  `;
  tbody.insertBefore(newSection, tbody.firstChild);
  const fileInputs = document.querySelectorAll('.br-input');
  const noFileTexts = document.querySelectorAll('.btn.get-start.browse-btn');
  console.log(fileInputs,noFileTexts);
  fileInputs.forEach((input, index) => {
    input.addEventListener('change', (event) => {
      const fileName = event.target.files.length > 0 ? event.target.files[0].name.slice(0,12) : 'Choose file';
      noFileTexts[index].lastChild.textContent = fileName; // Update the text to show the selected file name
    });
  });
  // Append the new slide to the beginning of the table
  

  // Increment the slide counter for future slides
  slideCounter++;
});

const fileInputs = document.querySelectorAll('.br-input');
const noFileTexts = document.querySelectorAll('.btn.get-start.browse-btn');
console.log(fileInputs,noFileTexts);
fileInputs.forEach((input, index) => {
  input.addEventListener('change', (event) => {
    const fileName = event.target.files.length > 0 ? event.target.files[0].name.slice(0,12) : 'Choose file';
    noFileTexts[index].lastChild.textContent = fileName; // Update the text to show the selected file name
  });
});


// Smooth scrolling for anchor links

// JavaScript to handle the active class on nav links
const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".navbar-nav a");

window.addEventListener("scroll", () => {
  let current = "";

  sections.forEach((section) => {
    const sectionTop = section.offsetTop;
    const sectionHeight = section.clientHeight;

    if (pageYOffset >= sectionTop - sectionHeight / 3) {
      current = section.getAttribute("id");
    }
  });

  navLinks.forEach((link) => {
    link.classList.remove("active");
    if (link.getAttribute("href") === `#${current}`) {
      link.classList.add("active");
    }
  });
});

// Wait until the DOM is fully loaded


const sliderThumb = document.getElementById("sliderThumb");
      const sliderFilled = document.getElementById("slider-filled");
      const valueLabel = document.getElementById("valueLabel");
      const valuescrollId = document.getElementById("valuescrollId");
      const sliderContainer = document.querySelector(".slider-container");
      const trackWidth = sliderContainer.offsetWidth;

      let isDragging = false;
      sliderThumb.style.left = "20%";
      sliderFilled.style.width = "20%";
      // Define min and max values for the slider
      const minValue = 0;
      const maxValue = 100;
// Set initial value (20% of maxValue)
      function updateSliderPosition(event) {
  if (isDragging) {
    const rect = sliderContainer.getBoundingClientRect();
    const offsetX = event.clientX - rect.left; // Get the mouse position relative to the slider
    const percentage = Math.max(0, Math.min(offsetX / trackWidth, 1)); // Calculate the percentage
    const value = Math.round(
      percentage * (maxValue - minValue) + minValue
    ); // Convert to 0-100 scale
    const thumbX = percentage * (trackWidth - sliderThumb.offsetWidth); // Calculate thumb position

    // Update the thumb position and the label value
    sliderThumb.style.left = `${percentage * 100}%`;
    sliderFilled.style.width = `${percentage * 100}%`;
    valueLabel.innerHTML = `${value}%`; // Append percentage symbol
    valuescrollId.value=`${value}`
    // Optionally update other elements, e.g., the font size of an element
    textAreaFont.style.fontSize = `${value}px`;
  }
}
      // Mouse down event to start dragging
      sliderThumb.addEventListener("mousedown", () => {
        isDragging = true;
      });

      // Mouse up event to stop dragging
      document.addEventListener("mouseup", () => {
        isDragging = false;
      });

      // Mouse move event to update the slider
      document.addEventListener("mousemove", updateSliderPosition);


      // Function to create watermark text elements
function createWatermarkText(text) {
  const watermark = document.createElement('div');
  watermark.className = 'watermark';
  watermark.textContent = text;

  // Randomize position within the container
  const container = document.querySelector('.image-container');
  const containerWidth = container.offsetWidth;
  const containerHeight = container.offsetHeight;

  // Generate random position
  const x = Math.random() * (containerWidth - 200); // Adjust -200 for text width
  const y = Math.random() * (containerHeight - 50); // Adjust -50 for text height

  watermark.style.left = `${x}px`;
  watermark.style.top = `${y}px`;

  container.appendChild(watermark);
}

// Add multiple watermark texts
const numberOfWatermarks = 10; // Set the number of text instances
const sampleText = "LeadMaker.io";

for (let i = 0; i < numberOfWatermarks; i++) {
  createWatermarkText(sampleText);
}
const form = document.querySelector('.lead-form');
console.log(form);
function showLoadingAndRedirect(event) {
    event.preventDefault(); // Prevent default click behavior
  
    // Show the loading block
    // document.querySelector('.load').style.display = 'block';
    // document.querySelector('.contain').style.display = 'none';
  
    // // Optional: Add some dots animation
    // let dots = 0;
    // const loadingText = document.querySelector('.lead-title .dots');
    // const interval = setInterval(() => {
    //     dots = (dots + 1) % 4; // Cycle through 0 to 3
    //     loadingText.textContent = '.'.repeat(dots); // Update dots
    // }, 500);
    // Submit the form programmatically after a short delay
    const form = document.querySelector('.lead-form'); // Select the form
    form.submit();
    
    setTimeout(() => {
      clearInterval(interval);
   // Submit the form
    }, 3000); // Adjust delay if needed
  }
form.addEventListener('submit', showLoadingAndRedirect);