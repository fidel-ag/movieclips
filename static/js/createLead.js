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
    // setTimeout(() => {
    //   clearInterval(interval);
    //   const form = document.querySelector('.lead-form'); // Select the form
    //   form.submit(); // Submit the form
    // }, 3000); // Adjust delay if needed
  }

document.addEventListener('DOMContentLoaded', function () {
    updateSlideNumbers();
});
function updateSlideNumbers() {
    const rows = document.querySelectorAll('#leadsTable tbody tr');
    rows.forEach((row, index) => {
        row.cells[0].innerText = `Slide ${index + 1}`;
    });
}

function addSlide() {
    var table = document.getElementById('leadsTable').getElementsByTagName('tbody')[0];
    var newRow = table.insertRow(0);
    var slideCell = newRow.insertCell(0);
    slideCell.innerText = `Slide ${table.rows.length + 1}`;
    newRow.innerHTML += 
        `<td>
          <textarea style="font-size: 19px;" type="text" name="slide_text[]" value="" placeholder="Type Your Sentence Here" class="form-control tab-textarea" aria-describedby="textarea"></textarea>
        </td>
        <td style="background: none;">
           <div class="custum-browse custum-browse-v2 d-flex align-items-center">
             <div class="brws">
               <input class="br-input" type="file" name="slide_image[]" >
                  <a href="#!" class="btn get-start browse-btn">
                 <img src="./static/images/upload-icn-black.svg" alt=""> Choose file
               </a>
             </div>
            
           </div>
         </td>
         <td>
                <a href="#!" class="delete-row-btn" onclick="deleteSlide(this)">
                  <img src='static/images/delete-icn.svg' alt="delete" />
                </a>
         </td>`;
    const fileInputs = document.querySelectorAll('.br-input');
    const noFileTexts = document.querySelectorAll('.btn.get-start.browse-btn');
    console.log(fileInputs,noFileTexts);
    fileInputs.forEach((input, index) => {
      input.addEventListener('change', (event) => {
        const fileName = event.target.files.length > 0 ? event.target.files[0].name : 'Choose file';
        noFileTexts[index].lastChild.textContent = fileName; // Update the text to show the selected file name
      });
    });
    updateSlideNumbers();
}

function deleteSlide(btn) {
    var row = btn.parentNode.parentNode;
    row.parentNode.removeChild(row);
    updateSlideNumbers();
}

const form = document.querySelector('.lead-form');
console.log(form);
form.addEventListener('submit', showLoadingAndRedirect);

