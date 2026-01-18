'use client';

import { useState } from 'react'
import './App.css'
import Wave from 'react-wavify'

function HomePage() {
  const [activePage, setActivePage] = useState('dashboard')

  const stats = [
    { label: 'Incidents Prevented', value: '1,247', change: '+12.5% from last month' },
    { label: 'Active Locations', value: '48', change: '+3 new this quarter' },
    { label: 'Detection Rate', value: '94.2%', change: '+2.1% improvement' },
    { label: 'Staff Trained', value: '312', change: '+28 this month' },
  ]

  const activities = [ //change type to correspond to severity
    { type: 'alert', title: 'GOY DETECTED', meta: 'Store #127 - 5 minutes ago' },
    { type: 'alert', title: 'Penny Stolen', meta: 'Store #089 - 23 minutes ago' },
    { type: 'suspicious', title: 'Unknown', meta: 'Store #045 - 1 hour ago' },
    { type: 'direAlert', title: 'y/n detected', meta: 'System - 2 hours ago' },
  ]
  

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
              {activities.map((activity, index) => (
                <div key={index} className="activityItem">
                  <div className={`activityIcon ${activity.type}`}>
                    {activity.type === 'direAlert' && '!!!'}
                    {activity.type === 'alert' && '!'}
                    {activity.type === 'suspicious' && '?'}
                  </div>
                  <div className="activityContent">
                    <div className="activityTitle">{activity.title}</div>
                    <div className="activityMeta">{activity.meta}</div>
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
                    <div className="statGridItemVideo"><video src='https://files.catbox.moe/dfs93t.mp4' controls></video></div>
                    <div className="statGridItem">hi</div>
                </div>
              </div>
        </div>
      </div>
      
    </div>
    
  )
}

export default HomePage
