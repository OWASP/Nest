import { IconProp } from '@fortawesome/fontawesome-svg-core';
import Tooltip from '@mui/material/Tooltip';
import React, { JSX } from 'react';
import type { Issue } from 'types/issue';
import type { Milestone } from 'types/milestone';
import type { PullRequest } from 'types/pullRequest';
import type { Release } from 'types/release';
import SecondaryCard from 'components/SecondaryCard';
import { TruncatedText } from 'components/TruncatedText';

const ItemCardList = ({
  title,
  data,
  icon,
  renderDetails,
  showAvatar = true,
  showSingleColumn = true,
}: {
  title: React.ReactNode;
  data: Issue[] | Milestone[] | PullRequest[] | Release[];
  icon?: IconProp;
  showAvatar?: boolean;
  showSingleColumn?: boolean;
  renderDetails: (item: {
    createdAt: string;
    commentsCount: number;
    organizationName: string;
    publishedAt: string;
    repositoryName: string;
    tagName: string;
    openIssuesCount: number;
    closedIssuesCount: number;
    author: {
      avatarUrl: string;
      login: string;
      name: string;
    };
  }) => JSX.Element;
}) => (
  <SecondaryCard icon={icon} title={title}>
    {data && data.length > 0 ? (
      <div
        className={`grid ${
          showSingleColumn
            ? 'grid-cols-1'
            : 'gap-4 gap-y-0 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
        }`}
        data-testid="item-list"
      >
        {data.map((item, index) => (
          <div
            key={index}
            data-testid="item-card"
            className="mb-4 w-full rounded-lg bg-gray-200 p-4 dark:bg-gray-700"
          >
            <div className="flex w-full flex-col justify-between">
              <div className="flex w-full items-center">
                {showAvatar && item?.author?.avatarUrl && (
                  <Tooltip
                    title={item?.author?.name || item?.author?.login}
                    placement="bottom"
                  >
                    <a
                      className="flex-shrink-0 text-blue-400 hover:underline"
                      href={`/members/${item?.author?.login}`}
                    >
                      <img
                        height={24}
                        width={24}
                        src={item?.author?.avatarUrl}
                        alt={item?.author?.name || ''}
                        className="mr-2 rounded-full"
                      />
                    </a>
                  </Tooltip>
                )}
                <h3 className="flex-1 overflow-hidden text-ellipsis whitespace-nowrap font-semibold">
                  <a
                    className="text-blue-400 hover:underline"
                    href={item?.url || ''}
                    target="_blank"
                    rel="noopener noreferrer"
                    data-testid="item-link"
                  >
                    <TruncatedText text={item.title || item.name} />
                  </a>
                </h3>
              </div>
              <div className="ml-0.5 w-full" data-testid="item-details">
                {renderDetails(item)}
              </div>
            </div>
          </div>
        ))}
      </div>
    ) : (
      <p data-testid="empty-message">Nothing to display.</p>
    )}
  </SecondaryCard>
);

export default ItemCardList;