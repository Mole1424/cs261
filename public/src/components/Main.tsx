import React, {useEffect, useState} from "react";
import {IUserData} from "../types/IUserData";
import {requestLogout} from "./Login";
import {ICbEvent, ILoadArticleEvent, ILoadCompanyEvent} from "../types/AppEvent";
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
import ArticleCard, {requestArticle} from "./ArticleCard";
import ViewNotifications from "./ViewNotifications";

interface IProps {
  user: IUserData;
  onLogout: () => void;
  defaultTab?: string; // Default tab to load in to.
  initialEvent?: ICbEvent; // Event to trigger immediately. Occurs _after_ defaultTab.
}

export const Main = ({ user, onLogout, defaultTab, initialEvent }: IProps) => {
  const [viewContent, setViewContent] = useState<React.JSX.Element | null>(null);
  const [selectedTab, setSelectedTab] = useState(-1);
  const cachedComponents: { [key: string]: React.JSX.Element } = {};

  useEffect(() => {
    // Initial event?
    if (initialEvent) {
      void handleCallback(initialEvent);
    }

    // Load default tab content? (event takes precedence)
    else if (defaultTab) {
      const defaultIndex = tabs.findIndex(tab => tab.label === defaultTab);
      setSelectedTab(defaultIndex);

      const tab = tabs[defaultIndex];
      if (tabs[defaultIndex]) {
        setCachedContent(tab.label, tab.generateContent);
      }
    }
  }, [initialEvent, defaultTab]);

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
  const handleCallback = async (event: ICbEvent) => {
    switch (event.type) {
      case 'load-company':
        const companyId = (event as ILoadCompanyEvent).companyId;
        setViewContent(<CompanyDetails user={user} companyId={companyId} eventCallback={handleCallback} />);
        setSelectedTab(-1);
        break;
      case 'load-article':
        const articleId = (event as ILoadArticleEvent).articleId;
        const response = await requestArticle(articleId);

        if (response && !response.error) {
          setViewContent(<main className={'content-cards'}>
            <div className={'cards'}>
              <ArticleCard article={response.data!} eventCallback={handleCallback} />
            </div>
          </main>);
          setSelectedTab(-1);
        } else {
          console.log("Failed to display article " + articleId);
        }

        break;
      case 'load-notifications':
        setViewContent(<ViewNotifications user={user} eventCallback={handleCallback} />);
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
            <NotificationBell user={user} eventCallback={handleCallback} />
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

export default Main;
