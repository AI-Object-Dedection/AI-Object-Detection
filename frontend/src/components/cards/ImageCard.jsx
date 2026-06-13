import React from 'react';
import './ImageCard.css';

const ImageCard = ({ 
  image, 
  onSelect, 
  isSelected = false,
  onClick 
}) => {
  const {
    thumbnail_url,
    category,
    uploaded_at,
    status,
    description,
    confidence,
    detected_objects
  } = image;

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  // detected_objects is a JSON string produced by the backend detector
  // (mock now, SAM3 later). Parse it into damage-class chips. Stays safe if
  // the field is empty or not yet analyzed.
  const parseDetected = (raw) => {
    if (!raw) return [];
    try {
      const parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;
      return Array.isArray(parsed?.classes) ? parsed.classes : [];
    } catch {
      return [];
    }
  };
  const detectedClasses = parseDetected(detected_objects);

  return (
    <div 
      className={`image-card ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
    >
      {onSelect && (
        <div 
          className="image-card-checkbox"
          onClick={(e) => {
            e.stopPropagation();
            onSelect(image);
          }}
        >
          <input 
            type="checkbox" 
            checked={isSelected}
            onChange={() => {}}
          />
        </div>
      )}
      
      <div className="image-card-thumbnail">
        <img src={thumbnail_url} alt={description || 'Site photo'} />
      </div>
      
      <div className="image-card-content">
        {status && (
          <span className={`image-card-status status-${status}`}>
            {status}
          </span>
        )}
        {category && (
          <span className="image-card-category">
            {category}
            {confidence != null && (
              <span className="image-card-confidence">
                {Math.round(confidence * 100)}%
              </span>
            )}
          </span>
        )}
        {detectedClasses.length > 0 && (
          <div className="image-card-damages">
            {detectedClasses.slice(0, 4).map((d) => (
              <span key={d.label} className="image-card-damage-chip">
                {d.label}
                {d.coverage != null && (
                  <em>{Math.round(d.coverage * 100)}%</em>
                )}
              </span>
            ))}
            {detectedClasses.length > 4 && (
              <span className="image-card-damage-chip more">
                +{detectedClasses.length - 4}
              </span>
            )}
          </div>
        )}
        <p className="image-card-date">{formatDate(uploaded_at)}</p>
        {description && (
          <p className="image-card-description">{description}</p>
        )}
      </div>
    </div>
  );
};

export default ImageCard;
