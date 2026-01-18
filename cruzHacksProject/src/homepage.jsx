'use client';

import { useState } from 'react'
import './App.css'
import Wave from 'react-wavify'
import axios from 'axios';
import { useEffect } from 'react';
import MuxPlayer from '@mux/mux-player-react';

function HomePage(userId) {
  const [activePage, setActivePage] = useState('dashboard')
  const [data, setData] = useState([])

  const baseURL = "/api"

  useEffect(() => {
    axios.get(`${baseURL}/test12345`) //hardcoded change to  axios.get(`${baseURL}/#{userId}`)
			.then(response => {
				const incidents = response.data
        console.log(incidents)
        console.log(response.status)
        setData(response)
      })
      .catch(error => {
        console.log(error)
      })
      
  }, ([userId]));

  const stats = [
    { label: 'Incidents Prevented', value: '1,247', change: '+12.5% from last month' },
    { label: 'Active Locations', value: '48', change: '+3 new this quarter' },
    { label: 'Detection Rate', value: '94.2%', change: '+2.1% improvement' },
    { label: 'Staff Trained', value: '312', change: '+28 this month' },
  ]

  // Map severity level to icon type
  const getSeverityType = (severity) => {
    if (severity >= 3) return 'direAlert'
    if (severity === 2) return 'alert'
    return 'suspicious'
  }

  // Convert API response data to incident format
  const incidents = data.data ? data.data.map(incident => ({
    type: getSeverityType(incident.severity),
    title: incident.incidentType,
    meta: `${incident.summary} - ${incident.timestamp}`,
    videoURL: incident.videoURL,
    severity: incident.severity
  })) : []
  

  //const now = new Date();
  //const twentyFourHoursAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

  //const recentEvents = activities.filter(activity => activity.time > twentyFourHoursAgo);
  //const totalRecentEvents = recentEvents.length;


  const totalRecentEvents = 0 //remind me to delet this once we get everything figured out

  
  return (
    <div className="viewArea">
      <div className="mainBox">
        <div className="leftBox">
          <h1 className="pageTitle">Loss Prevention Dashboard</h1>
          <p className="pageSubtitle"></p>
          
          {/*<div className="statsGrid">
            {stats.map((stat, index) => (<div key={index} className="statCard"><div className="statLabel">{stat.label}</div><div className="statValue">{stat.value}</div><div className="statChange">{stat.change}</div></div>))}
          </div>*/}

          <div className="activitySection">
            <h2 className="sectionTitle">Recent Activity</h2>
            <div className="activityList">
              {incidents.map((incident, index) => (
                <div key={index} className="activityItem">
                  <div className={`activityIcon ${incident.type}`}>
                    {incident.type === 'direAlert' && '!!!'}
                    {incident.type === 'alert' && '!'}
                    {incident.type === 'suspicious' && '?'}
                  </div>
                  <div className="activityContent">
                    <div className="activityTitle">{incident.title}</div>
                    <div className="activityMeta">{incident.meta}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        <div className="rightBox">
              <div className="statGriddy">
                <div className="topRow">
                    <div className="statGridItem">
                        <div className="recentWarningsSmall">
                            <img src={totalRecentEvents > 0 ? 'src/assets/alert.svg' : 'src/assets/check.svg'} />
                            <p>Issues Today : {totalRecentEvents}</p>
                        </div>
                    </div>
                    <div className="statGridItem">
                        <div className="liveFeeds">
                            <img src='src/assets/camera.svg'/> 
                            <p>View Live Feed</p>
                        </div>
                    </div>
                </div>
                  
                <div className="bottomRow">
                  
                    <div className="statGridItemVideo"> <MuxPlayer
      playbackId = {incidents[0].videoURL}
      metadata={{
        video_id: "video-id-54321",
        video_title: "Test video title",
        viewer_user_id: "user-id-007",
      }}
    /></div>
                    <div className="statGridItem">
                        {incidents.length > 0 && (
                          <div className="incidentDetails">
                            <p><strong>Type:</strong> {incidents[0].title}</p>
                            <p><strong>Severity:</strong> {incidents[0].severity}</p>
                            <p><strong>Details:</strong> {incidents[0].meta}</p>
                          </div>
                        )}
                    </div>
                </div>
              </div>
        </div>
      </div>
    </div>
    
  )
}

export default HomePage
