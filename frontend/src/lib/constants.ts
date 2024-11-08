export type IconType = {
  [key: string]: string | number;
};

export interface Level {
  color: string;
  icon: string;
  level?: string;
}

export type topContributorsType = {
  avatar_url: string;
  contributions_count: number;
  login: string;
  name: string;
}

export type ButtonType = {
  label: string;
  icon?: JSX.Element;
  onclick?: () => void;
  link?: string;
}

export interface CardProps {
  title: string;
  summary: string;
  level?: Level;
  icons?: IconType;
  leaders?: string[];
  topContributors?: topContributorsType[];
  topics?: string[];
  button: ButtonType;
  projectName?: string;
  projectLink?: string;
  languages?: string[];
  social?: { title: string, icon: string, url: string }[];
}

export const Icons = {
  idx_updated_at: {
    label: "Last update date",
    icon: "fa-solid fa-arrows-rotate",
  },
  idx_forks_count: {
    label: "GitHub forks count",
    icon: "fa-solid fa-code-fork",
  },
  idx_stars_count: {
    label: "GitHub stars count",
    icon: "fa-regular fa-star",
  },
  idx_contributors_count: {
    label: "GitHub contributors count",
    icon: "fa-regular fa-user",
  },
  idx_created_at : {
      label: "Creation date",
      icon: "fa-regular fa-clock",
  },
  idx_comments_count: {
    label: "Comments count",
    icon: "fa-regular fa-comment",
  }
};

export const level = {
  incubator: {
    color: "#53AAE5",
    icon: " text-white fa-solid fa-egg ",
    level: "Incubator",
  },
  lab: {
    color: "#FFA500",
    icon: " text-white fa-solid fa-flask",
    level: "Lab",
  },
  production: {
    color: "#800080",
    icon: " text-white fa-solid fa-city",
    level: "Production",
  },
  flagship: {
    color: "#38a047",
    icon: " text-white fa-solid fa-flag",
    level: "Flagship",
  },
};

export const urlMappings = [
    { key: 'youtube.com', title: 'YouTube', icon: "fa-brands fa-youtube" },
    { key: 'x.com', title: 'X (formerly Twitter)', icon: "fa-brands fa-x-twitter" },
    { key: 'google.com', title: 'Google', icon: "fa-brands fa-google" },
    { key: 'meetup.com', title: 'Meetup', icon: "fa-brands fa-meetup" },
    { key: 'linkedin.com', title: 'LinkedIn', icon: "fa-brands fa-linkedin" },
    { key: 'facebook.com', title: 'Facebook', icon: "fa-brands fa-facebook"},
    { key: 'discord.com', title: 'Discord', icon: "fa-brands fa-discord" },
    { key: 'slack.com', title: 'Slack', icon: "fa-brands fa-slack" }
];

export const tooltipStyle = {
  backgroundColor: "white",
  color: "black",
}
