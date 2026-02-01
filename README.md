This repo is just small microservice for my  <a href="https://github.com/saimahendra282/Serverless_P2P_Video_App.git" target="_blank">project</a> that handles webrtc logic in python language 

This repo handles handles:
1. Room creation
2. User presence tracking
3. Peer-to-peer signaling
4. Call request routing
   
<h2>Code Structure and Logic</h2>

<p>
This section explains the purpose and internal logic of the main functions used in this WebRTC signaling microservice.
</p>

<hr>

<h3>1. Application Initialization</h3>

<pre><code>app = FastAPI()</code></pre>

<p>
Initializes the FastAPI application that handles HTTP and WebSocket requests.
</p>

<p>
CORS middleware is enabled to allow frontend clients to communicate with the backend.
</p>

<hr>

<h3>2. In-Memory Data Storage</h3>

<p>
The application uses in-memory dictionaries to manage active connections and rooms.
</p>

<pre><code>active_rooms</code></pre>
<p>Stores created rooms and their metadata.</p>

<pre><code>room_connections</code></pre>
<p>Stores WebSocket connections per room.</p>

<pre><code>email_sockets</code></pre>
<p>Maps user emails to their WebSocket connections.</p>

<hr>

<h3>3. Room Creation API</h3>

<pre><code>@app.post("/create-room")</code></pre>

<p>
Creates a new communication room.
</p>

<p>
Logic:
</p>

<ul>
  <li>Checks if the room ID already exists.</li>
  <li>Stores room details in memory.</li>
  <li>Returns success or error response.</li>
</ul>

<hr>

<h3>4. Personal WebSocket Endpoint</h3>

<pre><code>@app.websocket("/ws-user/{email}")</code></pre>

<p>
Handles direct user-to-user signaling using email identifiers.
</p>

<p>
Logic:
</p>

<ul>
  <li>Accepts WebSocket connection.</li>
  <li>Closes any previous connection for the same email.</li>
  <li>Stores the active socket.</li>
  <li>Listens for signaling messages.</li>
  <li>Routes messages to target users.</li>
  <li>Removes socket on disconnect.</li>
</ul>

<p>
Supported message types:
</p>

<ul>
  <li>call-request</li>
  <li>call-accepted</li>
  <li>call-rejected</li>
</ul>

<hr>

<h3>5. Room Information API</h3>

<pre><code>@app.get("/room/{room_id}")</code></pre>

<p>
Returns metadata of an existing room.
</p>

<p>
Logic:
</p>

<ul>
  <li>Checks if room exists.</li>
  <li>Returns room details.</li>
  <li>Returns error if not found.</li>
</ul>

<hr>

<h3>6. Room WebSocket Signaling Endpoint</h3>

<pre><code>@app.websocket("/ws/{room_id}")</code></pre>

<p>
Handles WebRTC signaling between peers inside a room.
</p>

<p>
Logic:
</p>

<ul>
  <li>Accepts incoming connection.</li>
  <li>Adds socket to room connection list.</li>
  <li>Sends "init-call" when two peers are connected.</li>
  <li>Broadcasts signaling messages to other peers.</li>
  <li>Removes socket on disconnect.</li>
</ul>

<hr>

<h3>7. WebRTC Signaling Flow</h3>

<p>
The signaling server does not transmit media. It only exchanges connection metadata.
</p>

<ol>
  <li>Client joins a room.</li>
  <li>Server triggers call initialization.</li>
  <li>Clients exchange SDP offers and answers.</li>
  <li>ICE candidates are exchanged.</li>
  <li>Peer-to-peer connection is established.</li>
</ol>

<hr>

<h3>8. Error and Connection Handling</h3>

<p>
The server handles common runtime issues to maintain stability.
</p>

<ul>
  <li>Closes duplicate connections.</li>
  <li>Removes disconnected sockets.</li>
  <li>Prevents stale references.</li>
  <li>Handles malformed JSON safely.</li>
</ul>

<hr>

<h3>9. Current Limitations</h3>

<ul>
  <li>All data is stored in memory.</li>
  <li>Data is lost on server restart.</li>
  <li>No authentication system.</li>
  <li>No database persistence.</li>
  <li>Single-instance scalability.</li>
</ul>

<hr>

<h3>10. Recommended Improvements</h3>

<ul>
  <li>Add Redis for distributed state.</li>
  <li>Implement JWT authentication.</li>
  <li>Add database support.</li>
  <li>Enable horizontal scaling.</li>
  <li>Add structured logging.</li>
</ul>
