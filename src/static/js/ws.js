const protocol = window.location.protocol == "https:" ? "wss://" : "ws://";
const socket = new WebSocket(protocol + window.location.host + "/ws/notifier/");
socket.onopen = function open() {
  console.log("WebSockets connection created.");
};

socket.onmessage = function recieve(message) {
  const data = JSON.parse(message.data);
  const post = data.event;
  $.notifyClose();
  $.notify(
    {
      // options
      title: "new post collected",
      message: ",click to see it.",
      url: `/post/${post.id}`,
      target: "_blank",
    },
    {
      // settings
      type: "success",
      allow_dismiss: true,
      newest_on_top: true,
      placement: {
        from: "bottom",
        align: "center",
      },
      delay: 0,
    }
  );

  if (window.location.pathname == "/home/" || window.location.pathname == "/") {
    $(".row.infinite-container").prepend(`
          <div class="col-12 col-md-6 col-lg-4 infinite-item">
            <div class="post">
              <div class="post__img">
                ${post.thumnail_photo}
              </div>
              <div class="post__meta">
                  <span>${post.created_at}</span>
                  <span>author : ${post.author_screen_name}</span>
              </div>
              <h3 class="post__title" ${post.rtl ? 'style="direction: rtl; text-align: right;"' : ""}">${post.title}</h3>
              <div class="post__wrap">
                <a href="/post/${post.id}" class="post__link">Read more</a>
                <div class="post__comments">
                  <svg xmlns='http://www.w3.org/2000/svg' width='512' height='512' viewBox='0 0 512 512'>
                    <path d='M431,320.6c-1-3.6,1.2-8.6,3.3-12.2a33.68,33.68,0,0,1,2.1-3.1A162,162,0,0,0,464,215c.3-92.2-77.5-167-173.7-167C206.4,48,136.4,105.1,120,180.9a160.7,160.7,0,0,0-3.7,34.2c0,92.3,74.8,169.1,171,169.1,15.3,0,35.9-4.6,47.2-7.7s22.5-7.2,25.4-8.3a26.44,26.44,0,0,1,9.3-1.7,26,26,0,0,1,10.1,2L436,388.6a13.52,13.52,0,0,0,3.9,1,8,8,0,0,0,8-8,12.85,12.85,0,0,0-.5-2.7Z'
                      style='fill:none;stroke-linecap:round;stroke-miterlimit:10;stroke-width:32px'/>
                    <path d='M66.46,232a146.23,146.23,0,0,0,6.39,152.67c2.31,3.49,3.61,6.19,3.21,8s-11.93,61.87-11.93,61.87a8,8,0,0,0,2.71,7.68A8.17,8.17,0,0,0,72,464a7.26,7.26,0,0,0,2.91-.6l56.21-22a15.7,15.7,0,0,1,12,.2c18.94,7.38,39.88,12,60.83,12A159.21,159.21,0,0,0,284,432.11' 
                      style='fill:none;stroke-linecap:round;stroke-miterlimit:10;stroke-width:32px'/>
                  </svg>
                  0
                </div>
              </div>
            </div>
          </div>`);
  }
};
