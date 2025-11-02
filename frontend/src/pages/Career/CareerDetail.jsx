import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import FitScoreCard from '../../components/Career/FitScoreCard';
import CareerProgressionTimeline from '../../components/Career/CareerProgressionTimeline';
import EducationSection from '../../components/Career/EducationSection';
import ProConsSection from '../../components/Career/ProConsSection';
import RelatedCareersCarousel from '../../components/Career/RelatedCareersCarousel';

export default function CareerDetail() {
  const { careerId } = useParams();
  const [career, setCareer] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCareer = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_API_BASE_URL}/api/careers/get/${careerId}`
        );
        setCareer(response.data.career);
      } catch (error) {
        console.error('Failed to fetch career:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCareer();
  }, [careerId]);

  if (loading) return <div className="p-8 text-center">Loading...</div>;
  if (!career) return <div className="p-8 text-center">Career not found</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white p-8 mb-8">
        <div className="max-w-6xl mx-auto">
          <h1 className="text-4xl font-bold">{career.title}</h1>
          <p className="text-xl opacity-90">{career.category}</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto p-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Main content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Overview */}
            <div className="bg-white rounded-2xl p-8 shadow-lg">
              <h2 className="text-2xl font-bold mb-4">Overview</h2>
              <p className="text-gray-700 text-lg">{career.description}</p>
            </div>

            {/* BLOCK 2 Components */}
            <EducationSection career={career} />
            <ProConsSection career={career} />
            <CareerProgressionTimeline career={career} />
            <RelatedCareersCarousel career={career} />
          </div>

          {/* Right: Sidebar */}
          <div className="space-y-6">
            <FitScoreCard career={career} userSkills={[]} />
          </div>
        </div>
      </div>
    </div>
  );
}
