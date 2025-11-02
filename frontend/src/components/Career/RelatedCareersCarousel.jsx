import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Zap, ArrowRight } from 'lucide-react';

export default function RelatedCareersCarousel({ career, onCareerSelect }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const carouselRef = React.useRef(null);

  const relatedCareers = career?.related_careers || [
    { id: 1, title: 'Software Architect', description: 'Design scalable systems', fit_score: 92, skills: 'Design, Leadership' },
    { id: 2, title: 'DevOps Engineer', description: 'Infrastructure automation', fit_score: 88, skills: 'Infrastructure, Automation' },
    { id: 3, title: 'Technical Lead', description: 'Team leadership focus', fit_score: 85, skills: 'Leadership, Mentoring' }
  ];

  useEffect(() => {
    checkScroll();
    const container = carouselRef.current;
    container?.addEventListener('scroll', checkScroll);
    return () => container?.removeEventListener('scroll', checkScroll);
  }, []);

  const checkScroll = () => {
    if (carouselRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = carouselRef.current;
      setCanScrollLeft(scrollLeft > 0);
      setCanScrollRight(scrollLeft < scrollWidth - clientWidth - 10);
    }
  };

  const scroll = (direction) => {
    if (carouselRef.current) {
      const scrollAmount = 350;
      carouselRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
      setTimeout(checkScroll, 300);
    }
  };

  const getFitColor = (score) => {
    if (score >= 85) return { bg: 'bg-green-100', text: 'text-green-800', badge: 'bg-green-500', light: 'from-green-50' };
    if (score >= 70) return { bg: 'bg-blue-100', text: 'text-blue-800', badge: 'bg-blue-500', light: 'from-blue-50' };
    if (score >= 55) return { bg: 'bg-yellow-100', text: 'text-yellow-800', badge: 'bg-yellow-500', light: 'from-yellow-50' };
    return { bg: 'bg-gray-100', text: 'text-gray-800', badge: 'bg-gray-500', light: 'from-gray-50' };
  };

  if (!relatedCareers || relatedCareers.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-900">Related Career Paths</h2>
        <p className="text-gray-500 mt-4">No related careers data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8">
      <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center gap-3">
        <Zap className="w-8 h-8 text-indigo-600" />
        Related Career Paths
      </h2>

      {/* Carousel */}
      <div className="relative">
        {/* Navigation buttons */}
        {canScrollLeft && (
          <button
            onClick={() => scroll('left')}
            className="absolute left-0 top-1/2 -translate-y-1/2 -translate-x-4 z-10 bg-indigo-600 text-white p-3 rounded-full hover:bg-indigo-700 transition-all shadow-lg hover:shadow-xl"
            aria-label="Scroll left"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
        )}

        {canScrollRight && (
          <button
            onClick={() => scroll('right')}
            className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-4 z-10 bg-indigo-600 text-white p-3 rounded-full hover:bg-indigo-700 transition-all shadow-lg hover:shadow-xl"
            aria-label="Scroll right"
          >
            <ChevronRight className="w-6 h-6" />
          </button>
        )}

        {/* Carousel Container */}
        <div
          ref={carouselRef}
          className="flex overflow-x-auto scroll-smooth gap-6 pb-4 px-2 no-scrollbar"
        >
          {relatedCareers.map((relatedCareer, i) => {
            const colors = getFitColor(relatedCareer.fit_score || 75);
            return (
              <div
                key={relatedCareer.id || i}
                className="flex-shrink-0 w-80 bg-gradient-to-br from-indigo-600 to-blue-600 text-white rounded-2xl p-6 hover:shadow-2xl transition-all cursor-pointer transform hover:scale-105"
                onClick={() => onCareerSelect && onCareerSelect(relatedCareer)}
              >
                <h3 className="text-2xl font-bold mb-3">{relatedCareer.title}</h3>
                <p className="text-indigo-100 mb-4 text-sm">{relatedCareer.description}</p>

                {/* Skills */}
                <div className="mb-4 flex flex-wrap gap-2">
                  {(relatedCareer.skills?.split(',') || []).slice(0, 2).map((skill, si) => (
                    <span key={si} className="px-2 py-1 bg-white bg-opacity-20 rounded text-xs font-semibold">
                      {skill.trim()}
                    </span>
                  ))}
                </div>

                {/* Fit Score */}
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex-1 bg-white bg-opacity-20 rounded-full h-2">
                    <div
                      className="bg-white h-2 rounded-full transition-all"
                      style={{ width: `${relatedCareer.fit_score || 75}%` }}
                    ></div>
                  </div>
                  <span className="text-lg font-bold">{relatedCareer.fit_score || 75}%</span>
                </div>

                {/* CTA */}
                <button className="w-full mt-4 flex items-center justify-center gap-2 bg-white text-indigo-600 font-bold py-2 rounded-lg hover:bg-indigo-50 transition-colors">
                  Explore <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            );
          })}
        </div>
      </div>

      {/* Info text */}
      <div className="mt-6 p-4 bg-indigo-50 rounded-lg border-l-4 border-indigo-500">
        <p className="text-indigo-900 text-sm">
          💡 <strong>Tip:</strong> Swipe through related careers with similar skill requirements and progression paths.
        </p>
      </div>

      {/* CSS for scrollbar hiding */}
      <style>{`
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
        .no-scrollbar {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
}
