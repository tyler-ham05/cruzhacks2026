import { useLocation, useNavigate } from "react-router-dom";
import './incident.css';
import MuxPlayer from '@mux/mux-player-react';

function IncidentDetails() {
  const { state } = useLocation();
  const navigate = useNavigate();
  console.log(state);
  if (!state) {
    return <p className="error">ERROR: No incident data.</p>;
  }

  return (
    <div className="fullView2">
      <div className="mainBox2">
        <div className="videoSection">
          {state.videoURL && (
            <MuxPlayer
              playbackId={state.videoURL}
              metadata={{
                video_id: 'video-id-54321',
                video_title: state.title,
                viewer_user_id: 'user-id-007',
              }}
              autoplay={false}
              loop={false}
              muted={false}
              controls={true}
              className="muxPlayer"
            />
          )}
        </div>

        <div className="infoSection">
          <button className="backButton" onClick={() => navigate(-1)}>← Back</button>
          <h1>{state.title}</h1>
          <p><strong>Severity:</strong> {state.severity}</p>
          <p><strong>Details:</strong> {state.meta}</p>
          <p><strong>Description:</strong> {state.meta} probably lomger desc will go here</p>
        </div>
      </div>
    </div>
  );
}

export default IncidentDetails;