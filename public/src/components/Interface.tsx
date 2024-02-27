import React, {useEffect, useState} from "react";
import {IUserData} from "../types/IUserData";
import {requestLogout} from "./Login";
import {ICbEvent, ILoadCompanyEvent} from "../types/AppEvent";
import CompanyDetails from "./CompanyDetails";
import UserProfile from "./UserProfile";
import TabGroup, {ITab} from "./TabGroup";
import ViewFollowing from "./ViewFollowing";
import ViewForYou from "./ViewForYou";
import ViewRecent from "./ViewRecent";
import ViewPopular from "./ViewPopular";
import ViewSearch from "./ViewSearch";
import {APP_NAME} from "../index";
import NotificationBell from "./NotificationBell";

interface IProps {
  user: IUserData;
  onLogout: () => void;
  defaultTab?: string;
}

export const Interface = ({ user, onLogout, defaultTab }: IProps) => {
  const [viewContent, setViewContent] = useState<React.JSX.Element | null>(null);
  const [selectedTab, setSelectedTab] = useState(-1);
  const cachedComponents: { [key: string]: React.JSX.Element } = {};

  useEffect(() => {
    // Load default tab content?
    if (defaultTab) {
      const defaultIndex = tabs.findIndex(tab => tab.label === defaultTab);
      setSelectedTab(defaultIndex);

      const tab = tabs[defaultIndex];
      if (tabs[defaultIndex]) {
        setCachedContent(tab.label, tab.generateContent);
      }
    }
  }, []);

  /** Click the user's name */
  const setCachedContent = (key: string, generator: () => React.JSX.Element) => {
    if (key in cachedComponents) {
      setViewContent(cachedComponents[key]);
    } else {
      const content = generator();
      setViewContent(content);
      cachedComponents[key] = content;
    }
  };

  /** Callback: send event to load dynamic content. */
  const handleCallback = (event: ICbEvent) => {
    switch (event.type) {
      case 'load-company':
        const companyId = (event as ILoadCompanyEvent).companyId;
        setViewContent(<CompanyDetails companyId={companyId} />);
        setSelectedTab(-1);
        break;
      default:
        console.log(`Event: unknown event type ${event.type}`);
    }
  };

  /** Click on the username. */
  const clickUserName = () =>
    setCachedContent("user-profile", () =>
      <UserProfile user={user} />
    );

  /** Click on the notification bell. */
  const clickNotificationBell = () => {
    // TODO
    console.log("Click notification bell");
  };

  const tabs: (ITab & { generateContent: () => React.JSX.Element })[] = [
    {
      label: 'Following',
      generateContent: () => <ViewFollowing user={user} eventCallback={handleCallback} />,
      async onClick() {
        setCachedContent(this.label, this.generateContent);
        return { select: true };
      }
    },
    {
      label: 'For You',
      generateContent: () => <ViewForYou user={user} eventCallback={handleCallback} />,
      async onClick() {
        setCachedContent(this.label, this.generateContent);
        return { select: true };
      }
    },
    {
      label: 'Recent',
      generateContent: () => <ViewRecent user={user} eventCallback={handleCallback} />,
      async onClick() {
        setCachedContent(this.label, this.generateContent);
        return { select: true };
      }
    },
    {
      label: 'Popular',
      generateContent: () => <ViewPopular user={user} eventCallback={handleCallback} />,
      async onClick() {
        setCachedContent(this.label, this.generateContent);
        return { select: true };
      }
    },
    {
      label: 'Search',
      generateContent: () => <ViewSearch user={user} eventCallback={handleCallback} />,
      async onClick() {
        setCachedContent(this.label, this.generateContent);
        return { select: true };
      }
    },
    {
      label: 'Logout',
      generateContent: () => <></>, // Unused
      async onClick() {
        if (await requestLogout()) {
          onLogout();
        }

        return { select: false };
      }
    }
  ];

  return (
    <>
      <header>
        <div>
          <div>
            <span>
              {APP_NAME}
            </span>
          </div>
          <div>
            <span onClick={clickUserName}>
              {user.name}
            </span>
            <NotificationBell user={user} onClick={clickNotificationBell} />
          </div>
        </div>
        <TabGroup
          tabs={tabs}
          selected={selectedTab}
        />
      </header>
      {viewContent}
    </>
  );
};

export default Interface;
